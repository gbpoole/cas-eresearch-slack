# Install on a VM

* Copy a valid github key to the VM with: scp KEYNAME* ubuntu@IP_ADDRESS:/home/ubuntu/.ssh/
* Start the ssh agent with: eval "$(ssh-agent)"
* Add the key to the agent: ssh-add .ssh/KEYNAME
* Clone the REPO: git clone git@github.com:gbpoole/cas-eresearch-slack.git
* Install Docker with: ./cas-eresearch-slack/scripts/install_Docker_on_Ubuntu.sh
