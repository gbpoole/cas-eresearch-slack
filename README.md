# Installation

## Nectar VM

### VM Config

The following instructions have been validated with a Nectar VM configured as follows:

Flavour Name: t3.xsmall
Image Name: NeCTAR Ubuntu 20.04 LTS (Focal) amd64
Security Groups: add the following group to the defaults:
ALLOW IPv4 22/tcp from 0.0.0.0/0
ALLOW IPv4 443/tcp from 0.0.0.0/0
ALLOW IPv4 80/tcp from 0.0.0.0/0
ALLOW IPv6 to ::/0
ALLOW IPv4 to 0.0.0.0/0
ALLOW IPv4 8080/tcp from 0.0.0.0/0

In what follows, you will need the following, once the VM is instantiated:

* IP Address: available from the dashboard
* A project password to access the NeCTAR Cloud using the OpenStack API.  From the dashboard: > Settings > Reset Password

### Repo install

* Copy a valid github key to the VM with: scp KEYNAME* ubuntu@IP_ADDRESS:/home/ubuntu/.ssh/
* Start the ssh agent with: eval "$(ssh-agent)"
* Add the key to the agent: ssh-add .ssh/KEYNAME
* Clone the REPO: git clone git@github.com:gbpoole/cas-eresearch-slack.git
* Optionally, if you will edit the code locally, you'll want to do the following:

git config --global user.name "Your Name"
git config --global user.email "your@email.address"
git config --global core.editor "vi"
git remote set-url origin git@github.com:gbpoole/cas-eresearch-slack.git

# Install requirements

* Install Docker with: sudo ./cas-eresearch-slack/scripts/install_Docker_on_Ubuntu.sh (enter y-and-return when prompted)
* Install Python with: sudo ./cas-eresearch-slack/scripts/install_Python_on_Ubuntu.sh (enter y-and-return when prompted)
* install the OpenStack client: sudo ./cas-eresearch-slack/scripts/install_OpenStack_client.sh

# Set-up DNS name

* Install Open Stack CLI client:
	* Obtain Open Stack rc file from the dashboard: from the top bar, click on email and then OpenStack rc file download
	* scp rc file to the VM: scp rc-file-name.sh ubuntu@IP_ADDRESS:/home/ubuntu/
	* source the file on the VM: . rc-file-name.sh (enter project password when asked)
* Execute the following with the client:
	* check that your project has the default zone as follows: $ openstack zone list
	* add a DNS record for your instance to the zone as follows: $ openstack recordset create <project>.cloud.edu.au. <instance name> --type A --record <instance IP addr>
		* If a "Duplicate RecordSet" error is thrown, then you need to delete the old one first: openstack recordset delete <project>.cloud.edu.au.  <instance name>.<project>.cloud.edu.au.
		* then, retry the openstack recordset create command above
	
	

			




