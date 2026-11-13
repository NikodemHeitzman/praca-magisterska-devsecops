<#
.SYNOPSIS
    Destroys the working layer (infra/terraform/work) and checks that nothing billable is left.

.DESCRIPTION
    End-of-session teardown (docs/adr/0019-srodowisko-efemeryczne-aws.md, docs/aws-konto.md):
      1. terraform destroy of work/ (the permanent layer shared/ is never touched),
      2. terraform state list of work/ must be empty,
      3. AWS check by tag Project=devsecops-thesis: no instance that is not terminated,
         no EBS volume, no VPC, no Elastic IP, no cleanup schedule (ADR-0034).
    Exit code 0 only when every check passes. Times are printed for docs/koszty.md and 4.2.

    Run in local PowerShell from the repository root or from infra/terraform. Needs Terraform
    1.17.1, AWS CLI v2 and the named profile of the IAM user terraform.

.EXAMPLE
    .\infra\terraform\teardown.ps1
.EXAMPLE
    .\infra\terraform\teardown.ps1 -AutoApprove
.EXAMPLE
    .\infra\terraform\teardown.ps1 -CheckOnly
#>
[CmdletBinding()]
param(
    [string]$AwsProfile = "devsecops-terraform",
    [string]$Region = "eu-north-1",
    [string]$Project = "devsecops-thesis",
    # Skip the confirmation prompt of terraform destroy.
    [switch]$AutoApprove,
    # Only run the checks (e.g. after the scheduled cleanup or a manual destroy).
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"
$workDir = Join-Path $PSScriptRoot "work"
$env:AWS_PROFILE = $AwsProfile
$env:AWS_REGION = $Region
$failures = New-Object System.Collections.Generic.List[string]

function Invoke-Aws {
    param([string[]]$Arguments)
    $output = & aws @Arguments --region $Region --output json
    if ($LASTEXITCODE -ne 0) {
        throw "aws $($Arguments -join ' ') failed with exit code $LASTEXITCODE"
    }
    if ([string]::IsNullOrWhiteSpace(($output -join ""))) { return $null }
    return ($output -join "`n") | ConvertFrom-Json
}

$started = Get-Date
Write-Host "teardown: profile $AwsProfile, region $Region, layer $workDir"

$identity = Invoke-Aws @("sts", "get-caller-identity")
Write-Host "teardown: caller $($identity.Arn)"

# 1. terraform destroy of the working layer.
if (-not $CheckOnly) {
    & terraform "-chdir=$workDir" init -input=false | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "terraform init failed" }

    $destroyArgs = @("-chdir=$workDir", "destroy", "-input=false")
    if ($AutoApprove) { $destroyArgs += "-auto-approve" }
    $destroyStarted = Get-Date
    & terraform @destroyArgs
    if ($LASTEXITCODE -ne 0) { throw "terraform destroy failed with exit code $LASTEXITCODE" }
    $destroySeconds = [math]::Round(((Get-Date) - $destroyStarted).TotalSeconds)
    Write-Host "teardown: terraform destroy took $destroySeconds s"
}

# 2. Empty state of the working layer.
$state = & terraform "-chdir=$workDir" state list
if ($LASTEXITCODE -ne 0) { throw "terraform state list failed" }
$state = @($state | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
if ($state.Count -gt 0) {
    $failures.Add("terraform state of work/ still lists $($state.Count) resource(s): $($state -join ', ')")
}

# 3. Nothing left in AWS. The tag filter also catches resources dropped from the state.
$tagFilter = "Name=tag:Project,Values=$Project"

$instances = Invoke-Aws @("ec2", "describe-instances", "--filters", $tagFilter,
    "Name=instance-state-name,Values=pending,running,shutting-down,stopping,stopped",
    "--query", "Reservations[].Instances[].InstanceId")
if (@($instances).Count -gt 0) { $failures.Add("instances: $(@($instances) -join ', ')") }

$volumes = Invoke-Aws @("ec2", "describe-volumes", "--filters", $tagFilter, "--query", "Volumes[].VolumeId")
if (@($volumes).Count -gt 0) { $failures.Add("EBS volumes: $(@($volumes) -join ', ')") }

$vpcs = Invoke-Aws @("ec2", "describe-vpcs", "--filters", $tagFilter, "--query", "Vpcs[].VpcId")
if (@($vpcs).Count -gt 0) { $failures.Add("VPCs: $(@($vpcs) -join ', ')") }

$addresses = Invoke-Aws @("ec2", "describe-addresses", "--filters", $tagFilter, "--query", "Addresses[].PublicIp")
if (@($addresses).Count -gt 0) { $failures.Add("Elastic IPs: $(@($addresses) -join ', ')") }

$schedules = Invoke-Aws @("scheduler", "list-schedules", "--name-prefix", $Project, "--query", "Schedules[].Name")
if (@($schedules).Count -gt 0) { $failures.Add("schedules: $(@($schedules) -join ', ')") }

$totalSeconds = [math]::Round(((Get-Date) - $started).TotalSeconds)
if ($failures.Count -gt 0) {
    Write-Host "teardown: FAILED after $totalSeconds s, still present:" -ForegroundColor Red
    $failures | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

Write-Host "teardown: OK after $totalSeconds s: state of work/ empty, no instance, volume, VPC, Elastic IP or schedule tagged Project=$Project" -ForegroundColor Green
Write-Host "teardown: permanent layer (state bucket, IAM users, budgets) is kept until E15-08"
exit 0
