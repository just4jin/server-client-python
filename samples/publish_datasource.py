####
# This script demonstrates how to use the Tableau Server Client
# to publish a datasource to a Tableau server. It will publish
# a specified datasource to the 'default' project of the provided site.
#
# Some optional arguments are provided to demonstrate async publishing,
# as well as providing connection credentials when publishing. If the
# provided datasource file is over 64MB in size, TSC will automatically
# publish the datasource using the chunking method.
#
# For more information, refer to the documentations:
# (https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api_ref_datasources.htm#publish_data_source)
#
# To run the script, you must have installed Python 3.5 or later.
####

import argparse
import getpass
import logging

import tableauserverclient as TSC


def main():
    parser = argparse.ArgumentParser(description='Publish a datasource to server.')
    parser.add_argument('--server', '-s', required=True, help='server address')
    parser.add_argument('--site', '-i', help='site name')
    parser.add_argument('--username', '-u', required=True, help='username to sign into server')
    parser.add_argument('--filepath', '-f', required=True, help='filepath to the datasource to publish')
    parser.add_argument('--logging-level', '-l', choices=['debug', 'info', 'error'], default='error',
                        help='desired logging level (set to error by default)')
    parser.add_argument('--as-job', '-a', help='Publishing asynchronously', action='store_true')
    parser.add_argument('--conn-username', help='connection username')
    parser.add_argument('--conn-password', help='connection password')
    parser.add_argument('--conn-embed', help='embed connection password to datasource', action='store_true')
    parser.add_argument('--conn-oauth', help='connection is configured to use oAuth', action='store_true')

    args = parser.parse_args()

    # Ensure that both the connection username and password are provided, or none at all
    if (args.conn_username and not args.conn_password) or (not args.conn_username and args.conn_password):
        parser.error("Both the connection username and password must be provided")

    password = getpass.getpass("Password: ")

    # Set logging level based on user input, or error by default
    logging_level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=logging_level)

    # Sign in to server
    tableau_auth = TSC.TableauAuth(args.username, password, site=args.site)
    server = TSC.Server(args.server, use_server_version=True)
    with server.auth.sign_in(tableau_auth):
        # Create a new datasource item to publish - empty project_id field
        # will default the publish to the site's default project
        new_datasource = TSC.DatasourceItem(project_id="")

        # Create a connection_credentials item if connection details are provided
        new_conn_creds = None
        if args.conn_username:
            new_conn_creds = TSC.ConnectionCredentials(args.conn_username, args.conn_password,
                                                       embed=args.conn_embed, oauth=args.conn_oauth)

        # Define publish mode - Overwrite, Append, or CreateNew
        publish_mode = TSC.Server.PublishMode.Overwrite

        # Publish datasource
        if args.as_job:
            # Async publishing, returns a job_item
            new_job = server.datasources.publish(new_datasource, args.filepath, publish_mode,
                                                 connection_credentials=new_conn_creds, as_job=True)
            print("Datasource published asynchronously. Job ID: {0}".format(new_job.id))
        else:
            # Normal publishing, returns a datasource_item
            new_datasource = server.datasources.publish(new_datasource, args.filepath, publish_mode,
                                                        connection_credentials=new_conn_creds)
            print("Datasource published. Datasource ID: {0}".format(new_datasource.id))


if __name__ == '__main__':
    main()
