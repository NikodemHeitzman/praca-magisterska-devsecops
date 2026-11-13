# Automatic cleanup (docs/adr/0034-automatyczne-sprzatanie-eventbridge-scheduler.md):
# a one-time EventBridge Scheduler schedule terminates the app instance instance_ttl_hours
# after the plan that created it. Only the instance is removed (EC2, public IPv4 and the
# root volume are the whole cost of this layer); the rest waits for terraform destroy.
# The instance survives if it carries the tag SkipCleanup=true (explicit deny below).

data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id

  # at() takes a local date-time without offset; plantimestamp() is UTC, and so is the
  # schedule time zone below, so daylight saving time does not matter.
  cleanup_at = formatdate("YYYY-MM-DD'T'hh:mm:ss", timeadd(plantimestamp(), "${var.instance_ttl_hours}h"))
}

# Execution role assumed by EventBridge Scheduler. Trust limited to schedules of this account
# in the default schedule group (confused deputy protection). aws:SourceArn must be the
# schedule group ARN; a schedule ARN or name prefix makes CreateSchedule fail with
# "The execution role you provide must allow AWS EventBridge Scheduler to assume the role".
data "aws_iam_policy_document" "scheduler_assume" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }

    condition {
      test     = "ArnEquals"
      variable = "aws:SourceArn"
      values   = ["arn:aws:scheduler:${var.region}:${local.account_id}:schedule-group/default"]
    }
  }
}

resource "aws_iam_role" "cleanup" {
  name               = "${var.name_prefix}-cleanup"
  description        = "EventBridge Scheduler: terminate the app instance after its time to live (ADR-0034)"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume.json
}

# The role can only terminate instances of this project in this region and account, and
# never an instance tagged SkipCleanup=true.
data "aws_iam_policy_document" "cleanup" {
  statement {
    sid       = "TerminateProjectInstances"
    actions   = ["ec2:TerminateInstances"]
    resources = ["arn:aws:ec2:${var.region}:${local.account_id}:instance/*"]

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/Project"
      values   = ["devsecops-thesis"]
    }
  }

  statement {
    sid       = "KeepInstancesMarkedSkipCleanup"
    effect    = "Deny"
    actions   = ["ec2:TerminateInstances"]
    resources = ["*"]

    condition {
      test     = "StringEquals"
      variable = "aws:ResourceTag/SkipCleanup"
      values   = ["true"]
    }
  }
}

resource "aws_iam_role_policy" "cleanup" {
  name   = "${var.name_prefix}-cleanup"
  role   = aws_iam_role.cleanup.id
  policy = data.aws_iam_policy_document.cleanup.json
}

resource "aws_scheduler_schedule" "cleanup" {
  name        = "${var.name_prefix}-cleanup"
  description = "Terminate ${aws_instance.app.id} ${var.instance_ttl_hours} h after creation unless tagged SkipCleanup=true (ADR-0034)"

  schedule_expression          = "at(${local.cleanup_at})"
  schedule_expression_timezone = "UTC"

  # A completed one-time schedule still counts against the account quota.
  action_after_completion = "DELETE"

  flexible_time_window {
    mode = "OFF"
  }

  # Universal target: the EC2 API is called directly, no Lambda function.
  target {
    arn      = "arn:aws:scheduler:::aws-sdk:ec2:terminateInstances"
    role_arn = aws_iam_role.cleanup.arn
    input    = jsonencode({ InstanceIds = [aws_instance.app.id] })

    # Few retries: a denied call (SkipCleanup=true) should not be repeated for a day.
    retry_policy {
      maximum_retry_attempts       = 2
      maximum_event_age_in_seconds = 3600
    }
  }

  # The time is fixed when the schedule is created. A new instance gets a new schedule; a
  # schedule that already ran (and deleted itself) is recreated by the next apply, which
  # therefore also extends the session by another instance_ttl_hours.
  lifecycle {
    ignore_changes       = [schedule_expression]
    replace_triggered_by = [aws_instance.app.id]
  }

  depends_on = [aws_iam_role_policy.cleanup]
}
