# Agency Tools
Tools that hopefully make our lives a little easier

## Simple CLI App Generator
A simple CLI to spit out boilerplate code for media walls and list feeds.

Example Usage:

    $> python streamhub-app-generator.py -n "strategy-prod.fyre.co" -s 340628 -a "custom-1393461312708" "custom-1393461312708" -t "wall"

Options/Help (e.g. -h):

    $> python streamhub-app-generator.py -h
        usage: streamhub-app-generator.py [-h] -n NETWORK -s SITE_ID -a ARTICLE_IDS
                                          [ARTICLE_IDS ...] -t APP_TYPE [-f FILENAME]
                                          [-v SDK_VERSION] [-w WALL_VERSION]

        A way to generate boilerplate code for media walls and list feeds

        optional arguments:
          -h, --help            show this help message and exit
          -n NETWORK, --network NETWORK
                                the network the app is for (e.g. example.fyre.co)
          -s SITE_ID, --site-id SITE_ID
                                the site id the app is for (e.g. 123456)
          -a ARTICLE_IDS [ARTICLE_IDS ...], --article-ids ARTICLE_IDS [ARTICLE_IDS ...]
                                article ids of the collections (e.g. article-id-1
                                article-id-2 article-id-3
          -t APP_TYPE, --app-type APP_TYPE
                                the type of app to be generated (current options are
                                only list and wall)
          -f FILENAME, --filename FILENAME
                                the output filename
          -v SDK_VERSION, --sdk-version SDK_VERSION
                                (optional - will attempt to use latest) which sdk
                                version you'd like to use
          -w WALL_VERSION, --wall-version WALL_VERSION
                                (optional - will attempt to use latest) which version
                                of the medi wall you want to use

## Upload to S3
A bash script that will upload files to S3 for us. The benefit of this script, though, is that it will set the max-age header on EVERYTHING you upload.. which is way nice since you have to set it on each individual item uploaded. Additionally, it gzips for you (optionally, of course)!

Pre-req:
* You need s3cmd installed

        brew install s3cmd

* Configure s3cmd

        s3cmd --configure

It's going to then ask you to put your in your "access key" and "secret key". To get those, you should log on to a production box, run s3cmd and copy down the values (just press enter twice when prompted - IMPORTANT! Press ctrl + c after so that you don't actually save it).

Once you've entered the keys, press enter to all the prompts until it asks if you want to test the keys. Once it asks to test, just say "no" and then save.

* Running the command

        ./upload_to_s3.sh -b livefyre-nike-kd-ap-6 -s ../kd-aunt-pearl-6/ -i invalidation.txt -e gzip

Note, we gzip the contents.. so if you don't want that, don't put "-e gzip".
