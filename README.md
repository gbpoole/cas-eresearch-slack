# CAS-eResearch Slack Application

## Installation on Nectar VM

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

### VM Config

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
* Install the OpenStack client: sudo ./cas-eresearch-slack/scripts/install_OpenStack_client.sh
* Install certbot: sudo ./cas-eresearch-slack/scripts/install_certbot_on_Ubuntu.sh (enter y-and-return when prompted)
* Install Nginx: sudo ./cas-eresearch-slack/scripts/install_Nginx_on_Ubuntu.sh (enter y-and-return when prompted)

### Set-up DNS name

* Install Open Stack CLI client:
	* Obtain Open Stack rc file from the dashboard: from the top bar, click on email and then OpenStack rc file download
	* scp rc file to the VM: scp rc-file-name.sh ubuntu@IP_ADDRESS:/home/ubuntu/
	* source the file on the VM: . rc-file-name.sh (enter project password when asked)
* Execute the following with the client:
	* check that your project has the default zone as follows: $ openstack zone list
	* add a DNS record for your instance to the zone as follows: $ openstack recordset create <project>.cloud.edu.au. <instance name> --type A --record <instance IP addr>
		* If a "Duplicate RecordSet" error is thrown, then you need to delete the old one first: openstack recordset delete <project>.cloud.edu.au.  <instance name>.<project>.cloud.edu.au.
		* then, retry the openstack recordset create command above

### Set-up Nginx

* Verify that Nginx registered itself as a service with ufw when it installed: sudo ufw app list
	* You should see something like:

Available applications:
  Nginx Full
  Nginx HTTP
  Nginx HTTPS
  OpenSSH

* Verify that Nginx was started at the install: systemctl status nginx
	* You should see something like:

● nginx.service - A high performance web server and a reverse proxy server
     Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
     Active: active (running) since Wed 2022-08-03 04:35:19 UTC; 3min 17s ago
       Docs: man:nginx(8)
    Process: 44621 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
    Process: 44631 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
   Main PID: 44632 (nginx)
      Tasks: 2 (limit: 1144)
     Memory: 5.1M
     CGroup: /system.slice/nginx.service
             ├─44632 nginx: master process /usr/sbin/nginx -g daemon on; master_process on;
             └─44633 nginx: worker process

Aug 03 04:35:19 cas-eresearch-slack systemd[1]: Starting A high performance web server and a reverse proxy server...
Aug 03 04:35:19 cas-eresearch-slack systemd[1]: Started A high performance web server and a reverse proxy server.




### Set-up a "Let's Encrypt" Certificate



### Run the app

* Use docker-compose to start the app (from the repo directory): sudo docker-compose up -d
