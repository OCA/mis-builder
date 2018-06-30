Install the module in Odoo
==========================
If you already have an Odoo instance up and running, your preferred way to install
addons will work with `MIS Builder`.

Using git
---------
The most common way to install the module is to clone the git repository in your
server and add the directory to your odoo.conf:

#. Clone the git repository

   .. code-block:: sh

      cd your-addons-path
      git clone https://github.com/OCA/mis-builder
      cd mis-builder
      git checkout 10.0 #for the version 10.0

#. Update the addon path of `odoo.conf`
#. Restart Odoo
#. Update the addons list in your database
#. Install the MIS Builder application.

Using pip
---------
An easy way to install it with all its dependencies is using pip:

#. Recover the code from pip repository

   .. code-block:: sh

      pip install --pre odoo10-addon-mis_builder odoo-autodiscover

#. Restart Odoo
#. Update the addons list in your database
#. Install the MIS Builder application.

Fresh install with Docker
-------------------------
If you do not have any Odoo server installed, you can start your own Odoo in few
minutes via Docker in command line.

Here is the basic how-to (based on https://github.com/Elico-Corp/odoo-docker), valid
for Ubuntu OS but could also easily be replicated in MacOS or Windows:

#. Install docker and docker-compose in your system
#. Create the directory structure (assuming the base directory is `odoo`)

   .. code-block:: sh

      mkdir odoo && cd odoo
      mkdir -p ./volumes/postgres ./volumes/odoo/addons ./volumes/odoo/filestore \
      ./volumes/odoo/sessions

#. Create a `docker-compose.yml` file in `odoo` directory with following content:

   .. code-block:: xml

       version: '3.3'
       services:

         postgres:
           image: postgres:9.5
           volumes:
             - ./volumes/postgres:/var/lib/postgresql/data
           environment:
             - POSTGRES_USER=odoo

         odoo:
           image: elicocorp/odoo:11.0
           command: start
           ports:
             - 127.0.0.1:8069:8069
           volumes:
             - ./volumes/odoo/addons:/opt/odoo/additional_addons
             - ./volumes/odoo/filestore:/opt/odoo/data/filestore
             - ./volumes/odoo/sessions:/opt/odoo/data/sessions
           links:
             - postgres:db
           environment:
             - ADDONS_REPO=https://github.com/OCA/mis-builder.git
             - ODOO_DB_USER=odoo

#. Fire up your container (in `odoo` directory)

   .. code-block:: sh

      docker-compose up -d odoo

#. Open a web browser and navigate the URL you have set up in your `docker-compose.yml`
   file (http://127.0.0.1:8069 in this particular example)
#. Create a new database
#.  Update the addons list in your database (Menu `Apps > Update Apps List` in developer mode)
#. Install the MIS Builder application.
#. Improve your Odoo environment (add parameters, change default passwords etc.)
   under Docker: https://github.com/Elico-Corp/odoo-docker

More about `Odoo <https://www.odoo.com/documentation/11.0>`_.
