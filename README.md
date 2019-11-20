# jasper-release-import

Simple Python Script to deliver an Import package to a remote Jasper Report Server instance.

## Usage
The script accepts the following arguments:
 - **-user** (JS user)
 - **-org** (JS organization, can be ommited)
 - **-host** (JS remote host)
 - **-file** (Import .zip package)

### Example:


> python import.<span></span>py **-user** jasperadmin **-host** http://<span> **-</span>localhost:8080/jasperserver/ **-file** import_file.zip

