# Setting up the Avoor backend
This guide covers setting up the Avoor (Planbot+) backend server.

This guide was written with Linux and macOS in mind. If you're using Windows:
- replace `python3` with `python`,
- replace `pip3` with `pip`.

## Hosting the Avoor server
Avoor is designed to run on Google App Engine. For instructions see [Run on Google App Engine](#run-on-google-app-engine).

It will work on any other moderately fast web server that supports Python, but some features (e.g. email verification for registration) won't work without additional configuration. If you want to do this anyway or want to set it up for development, see [Do it yourself](#do-it-yourself).

## Optional: Set up a Google Cloud project
To access the Gemini API for AI-powered task management features, the Avoor backend needs a Google Cloud API key. A Google Cloud project is also necessary to host it on App Engine.

1. [Create a Google Cloud project](https://console.cloud.google.com/projectcreate) and enable billing.
2. Enable the following APIs:
    - [Identity and Access Management (IAM) API](https://console.cloud.google.com/flows/enableapi?apiid=iam.googleapis.com),
    - App Engine Admin API,
    - [Generative Language API](https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com?).
3. Go to [APIs & Services](https://console.cloud.google.com/apis/credentials) and create a new API key.
4. Click on the newly created API key.
5. Click "Restrict key" and select the Generative Language API.
6. Click OK.

## Run on Google App Engine
Make sure that you have already [set up a Google Cloud project](#optional-set-up-a-google-cloud-project).

### Set up App Engine

1. Go to [App Engine](https://console.cloud.google.com/appengine/start) and create an application.
2. Select a server region.
3. Wait until the application is created.
4. Install the Google Cloud SDK.

### Set up the Google Cloud Storage bucket
To serve images (profile pictures, etc.) Avoor uses the default bucket created when App Engine is set up. However, it has to be made public.

1. [Create an IAM role in Google Cloud](https://console.cloud.google.com/iam-admin/roles/create).
2. Enter any title and ID.
3. Under "Role launch stage", select "General Availability".
4. Click "Add permissions".
5. In the dialog that opens:
    - Enter `storage.objects.get` next to Filter and press Enter.
    - In the list below the Filter option, select `storage.objects.get`.
    - Click "Add".
6. Click "Create".
7. Go to the [Google Cloud Storage browser](https://console.cloud.google.com/storage/browser) and select the bucket that has the name of your project ID followed by "appspot.com".
    - At this point, you should only have 2 buckets - one starts with "staging." and the other doesn't. Select the one that **doesn't start with "staging"**.
8. Go to the "Permissions" tab.
9. Click "Remove public access prevention" and confirm.
9. Find "allUsers" in the table under "Permissions" and click on the pencil icon.
10. There should be a role called "Storage Object Viewer". Remove it.
11. Click "Add another role" and add the role created in step 5.
12. Click "Save changes".
13. Return to the "Objects" tab and create a folder called "static".

### Set up the server app
Before the server can be hosted on Google App Engine, the environment and database must be configured. This will be done on your computer.

1. Follow the Do it yourself guide on your local machine until step 3.
    - This is necessary to set up the environment and database.
    - As folder-based storage is incompatible with App Engine, set the environment variable `AVR_FS` to `google_bucket`.
    - Set `AVR_PORT` to `8080`.
2. Run `python3 setup.py -e`.

### Upload to Google App Engine
Here comes the fun part!

Run `gcloud app deploy` to upload the project to App Engine. If this is the first time that you're running the `gcloud` tool, you might need to sign in with your Google account and select the Google Cloud project to use.

After some time, you should see something that looks like this:
```
Services to deploy:

descriptor:                  [/workspace/app.yaml]
source:                      [/workspace]
target project:              [your-project-id]
target service:              [default]
target version:              [some-date]
target url:                  [https://your-project-id.region.r.appspot.com]
target service account:      [your-project-id@appspot.gserviceaccount.com]


Do you want to continue (Y/n)?
```

Press "Y".

After some more waiting, you should see something that looks like this:

```
Setting traffic split for service [default]....................................done.
Deployed service [default] to [https://your-project-id.region.r.appspot.com]

You can stream logs from the command line by running:
  $ gcloud app logs tail -s default

To view your application in the web browser run:
  $ gcloud app browse
```

The URL shown next to `Deployed service [default] to ` is the server's URL. If you open it in your browser, you should see the Avoor API home page. This is also the URL that should be provided to the app.

## Do it yourself
If you don't use a hosting platform or use an unsupported one, you can still set up Avoor.

First, download the Avoor repository or clone it using git; this folder will be known as the **root folder**.

It's recommended to use a virtual environment to isolate Avoor's dependencies from the dependencies of other apps:
```bash
$ pip3 install virtualenv
$ virtualenv avoor-env
# wait for the configuration to finish

# activate the virtual environment
$ source avoor-env/bin/activate
# or, if you're on Windows:
> avoor-env/Scripts/activate
```
If done correctly, the environment's name (`avoor-env` in this example) should appear at the start of the line. Proceed with the guide.

1. Install the dependencies:
```bash
$ pip3 install -r requirements.txt
```

2. Set the required environment variables. Unless stated otherwise, set secret strings to anything, well, secret - treat them like passwords.
- **AVR_DB_SK** - a secret string used for some database software.
- **AVR_DB_URL** - the URL or "connection string" of a database (MySQL, PostgreSQL...).
- **AVR_JW_SK** - a secret string used for generating authorization tokens.
- **AVR_PORT** - the port to run the API on. Defaults to `8000`.
    - The port can be found in the documentation of the hosting service or configuration of the reverse proxy/port forwarding software.
    - Some common ports include `8080` (used by Google App Engine and Amazon EC2) and `8000` (used by Azure).
- **AVR_SI_SK** - a secret string used for socket communication.
- **AVR_FS** - the storage method. Either:
    - `folder` - folder-based storage,
    - `google_bucket` - a Google Cloud Storage bucket.
        - Requires the variable `GOOGLE_CLOUD_PROJECT` to be set to the Google Cloud project ID. This is the case on App Engine but not on other platforms.
        - This uses the default Google App Engine bucket. If you aren't planning on using App Engine, create a Google Cloud Storage bucket called "(your project ID).appspot.com", then follow the steps in [Set up the Google Cloud Storage bucket](#set-up-the-google-cloud-storage-bucket) to configure access.
- **AVR_TK_SL** - a secret string used for generating email verification tokens.
- **AVR_EM_AD** - the email address to use for sending email verification tokens.
    - Note that only App Engine service accounts - any email address ending in `@(your project ID).appspotmail.com` - are supported.

> By default, AI responses will be replaced with placeholders. To use real responses generated using Gemini, [set up a Google Cloud project](#optional-set-up-the-google-cloud-project), then set the variable **AVR_AI** to `gemini` and  **AVR_GAK** to the created Google Cloud API key.

3. Set up the database:
```bash
flask --app server:create_flask_app db upgrade
```

4. Start the server:
```bash
$ python3 -m server
```
The server will start, and you should see something like this:
```
App Engine email detected. No password is required.
Starting event loop...
Created and started LRT event loop thread
INFO:     Waiting for application startup.
INFO:     ASGI 'lifespan' protocol appears unsupported.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

> Unless you're doing development, do not use `flask run` to run the Avoor server. It's OK for development but not recommended in any other case.
