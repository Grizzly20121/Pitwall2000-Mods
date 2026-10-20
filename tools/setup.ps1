$ErrorActionPreference='Stop'
$taskRepo='Grizzly20121/Pitwall2000-Mods'
$taskRoot=Split-Path $PSScriptRoot -Parent
Set-Location -LiteralPath $taskRoot
gh auth status
if($LASTEXITCODE -ne 0){throw 'GitHub CLI authentication is required.'}
$taskIdentity=gh api user --jq .login
if($taskIdentity -ne 'Grizzly20121'){throw 'Authenticated owner differs from the verified game remote owner.'}
$taskExisting=gh repo view $taskRepo --json visibility,nameWithOwner 2>$null
if($LASTEXITCODE -eq 0){
    if(($taskExisting|ConvertFrom-Json).visibility -ne 'PUBLIC'){throw 'Refusing to expose or reuse a private repository.'}
}else{
    gh repo create $taskRepo --public --description 'Pitwall 2000 data-only mod catalog, original examples and creator documentation'
    if($LASTEXITCODE -ne 0){throw 'Blocked operation: create public Grizzly20121/Pitwall2000-Mods.'}
}
python tools/package.py examples --all
if($LASTEXITCODE -ne 0){throw 'Source validation failed.'}
python tools/publish.py --tag examples-v1
if($LASTEXITCODE -ne 0){throw 'Release publication/public-byte verification failed; catalog was not published.'}
Write-Output 'Assets verified. Review catalog.json, commit only distribution files, then push main without force.'
