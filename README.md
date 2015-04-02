# VocaliD

1. [Install](#install)
1. [Run](#run)
1. [Work](#work)
1. [Wiki](https://github.com/vocalid/vocalid/wiki)

## Install

### git
---

    sudo apt-get -y install git

### GPG key
---

We use gpg to protect some sensitive data. You will need to generate a gpg key pair.

#### EITHER: Export and then import an already distributed key pair

    gpg --list-keys

It will display the key-id for the public key as follows.

    pub <some-code>/<key-id> <date>

You need the key-id for the public key.

Export a key pair.

    gpg --export -a <key-id> > <email>.pub
    gpg --export-secret-keys -a <key-id> > <email>

Import a key pair.

    gpg --import <email> <email>.pub

#### OR: Generate a new key pair and distribute it

    gpg --gen-key

It will display the key-id for the public key as follows.

    pub <some-code>/<key-id> <date>

You need the key-id for the public key.

##### Distribute the public key

    gpg --keyserver hkps.pool.sks-keyservers.net --send-keys <key-id>

Send the key-id by to the project lead as well.

The project lead will add your key to authorized.txt, and re-encrypt.

Proceed with the following **after** the project lead has done that.

### Code base
---

#### Get code base

    git clone https://github.com/vocalid/vocalid.git

#### Install on a developer machine

    cd vocalid/config

    bash setup.sh install

#### Install on an environment machine

    cd vocalid/config

    bash setup.sh -e prod|stage|test install

#### Customize config

Create environment-custom.py and system-custom.py to override any config.

## Run

#### Under Apache

    service apache2 restart

#### Under Gunicorn

    cd vocalid/run

    gunicorn -c gunicorn.py wsgi:application

#### Under Flask

    cd vocalid/run

    python wsgi.py

## Work

#### To checkout secrets.py

    cd vocalid/config

    bash setup.sh secrets.checkout

#### To checkin secrets.py

    cd vocalid/config

    bash setup.sh secrets.checkin
