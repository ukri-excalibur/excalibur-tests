# Getting Started on HPC systems

These tutorials have been ran in in-person workshops on various HPC systems in the UK. It should be possible to run on any of the [supported systems](../systems.md), or to [set up the tools](../setup.md) on a local machine. If you have access to one of the systems we've previously used, this tutorial helps you get set up. Otherwise, please consult the [documentation](../install.md)

## Connecting

=== "Cosma"

	To run these tutorials on Cosma, you need to [connect to Cosma via ssh](https://cosma.readthedocs.io/en/latest/ssh.html). You will need
	
	1. A Cosma account. You can [request a new account](https://cosma.readthedocs.io/en/latest/account.html) if you haven't got one you can use. You can use an existing Cosma account to complete the tutorials.
	2. A command line terminal with an ssh client. Most Linux and Mac systems come with these preinstalled. Please see [Connecting to ARCHER2](https://docs.archer2.ac.uk/user-guide/connecting/#command-line-terminal) for more information and Windows instructions.

=== "ARCHER2"
	To run these tutorials on ARCHER2, you need to [connect to ARCHER2 via ssh](https://docs.archer2.ac.uk/user-guide/connecting/). You will need

	1. An ARCHER2 account. You can [request a new account](https://docs.archer2.ac.uk/quick-start/quickstart-users/#request-an-account-on-archer2) if you haven't got one you can use. You can use an existing ARCHER2 account to complete the tutorials.
	2. A command line terminal with an ssh client. Most Linux and Mac systems come with these preinstalled. Please see [Connecting to ARCHER2](https://docs.archer2.ac.uk/user-guide/connecting/#command-line-terminal) for more information and Windows instructions.

----

### ssh

=== "Cosma"

	Please see [SSH access to Cosma](https://cosma.readthedocs.io/en/latest/ssh.html) for more information

=== "ARCHER2"
	Once you have the above prerequisites, you have to [generate an ssh key pair](https://docs.archer2.ac.uk/user-guide/connecting/#ssh-key-pairs) and [upload the public key to SAFE](https://docs.archer2.ac.uk/user-guide/connecting/#upload-public-part-of-key-pair-to-safe). 

	When you are done, check that you are able to connect to ARCHER2 with

	```bash
	ssh username@login.archer2.ac.uk
	```

----

### MFA

=== "Cosma"

	Cosma does not require MFA at present

=== "ARCHER2"

	ARCHER2 has deployed mandatory multi-factor authentication (MFA)

	SSH keys will work as before, but instead of your ARCHER2 password, a Time-based One-Time Password (TOTP) code will be requested. 

	TOTP is a six digit number, refreshed every 30 seconds, which is generated typically by an app running on your mobile phone or laptop.

	Thus authentication will require two factors:

	1) SSH key and passphrase
	2) TOTP

	The SAFE documentation which details how to set up MFA on machine accounts (ARCHER2) is available at:  
	[https://epcced.github.io/safe-docs/safe-for-users/#how-to-turn-on-mfa-on-your-machine-account](https://epcced.github.io/safe-docs/safe-for-users/#how-to-turn-on-mfa-on-your-machine-account)

	The documentation includes how to set this up without the need of a personal smartphone device.

	We have also updated the ARCHER2 documentation with details of the new connection process:  
	[https://docs.archer2.ac.uk/user-guide/connecting-totp/](https://docs.archer2.ac.uk/user-guide/connecting-totp/)  
	[https://docs.archer2.ac.uk/quick-start/quickstart-users-totp/](https://docs.archer2.ac.uk/quick-start/quickstart-users-totp/)  

	If there are any issues or concerns please contact support@archer2.ac.uk
