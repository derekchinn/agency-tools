## Simple CLI App Generator
    
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