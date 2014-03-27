import sys, itertools, os, argparse, urllib2, json, re

class Application_Type(object):
    LIST = "list"
    WALL = "wall"

class Application(object):
    LIST_TYPE = "list"
    WALL_TYPE = "wall"

    def __init__(self, network, site_id, article_id, instance_type):
        self.network = network
        self.site_id = site_id
        self.article_id = article_id
        self.instance_type = instance_type

    def build_view_fragment(self, var_id):
        """
        Builds the JS for the view
        """

        view_type_cc = ""
        view_type = ""
        el_prefix = ""

        if self.instance_type == Application_Type.LIST:
            view_type_cc = "listView"
            view_type = "ListView"
            el_prefix = "list"
        else:
            view_type_cc = "wallView"
            view_type = "WallView"
            el_prefix = "wall"

        js_view_var = "{}{}".format(view_type_cc, var_id)
        html_view_el = "{}-{}".format(el_prefix, var_id)

        template = """
            var {js_view_var} = new {view_type}({{
                initial: 50,
                showMore: 50,
                el: document.getElementById("{html_view_el}")
            }});
        """.format(js_view_var=js_view_var, view_type=view_type, html_view_el=html_view_el)

        return template, js_view_var, html_view_el

    def build_opts_fragment(self, var_id):
        """
        Build the opts for each application
        """

        template = """
            var opt{iter} = {{
                network: '{network}',
                siteId: '{site_id}',
                articleId: '{article_id}'
            }};
        """.format(iter=var_id, network=self.network, site_id=self.site_id, article_id=self.article_id)

        return template, "opt{}".format(var_id)

    def build_collection_fragment(self, var_id, opt_var, view_var):
        """
        Build the final js for connecting the collection with the view.
        """

        template = """
            var collection{iter} = new Collection({opt_var});
            collection{iter}.on("error", function (err) {{
                if (console) {{
                    console.log("Error just occurred: " + err);
                }}
            }});
            collection{iter}.pipe({view_var});
        """.format(iter=var_id, opt_var=opt_var, view_var=view_var)

        return template, "collection{}".format(var_id)

class Generator(object):
    def __init__(self, sdk_version, wall_version, filename="index.html", **kwargs):
        self.filename = filename
        self.sdk_version = sdk_version
        self.wall_version = wall_version
        self._apps = self._build_apps(**kwargs)
        self._app_types = self._generate_app_type_list(**kwargs)

    def _generate_app_type_list(self, **kwargs):
        """
        Figures out what kind of apps we have so that we can later add in the
        appropriate JS, CSS, and whatnot.
        """

        app_types = []

        if kwargs['list_article_ids']:
            app_types.append(Application_Type.LIST)

        if kwargs['wall_article_ids']:
            app_types.append(Application_Type.WALL)

        return app_types

    def _build_apps(self, list_article_ids, wall_article_ids, **kwargs):
        """
        Generates a list of apps so that we can use them later to build the right
        html and js.
        """

        apps = []

        if list_article_ids:
            for list_article_id in list_article_ids:
                apps.append(Application(article_id=list_article_id,
                                               instance_type=Application_Type.LIST,
                                               **kwargs))
        if wall_article_ids:
            for wall_article_id in wall_article_ids:
                apps.append(Application(article_id=wall_article_id,
                                               instance_type=Application_Type.WALL,
                                               **kwargs))

        return apps

    def _build_header(self):
        """
        Builds the header section for the html file
        """

        header = """
    <script src="http://cdn.livefyre.com/libs/sdk/{sdk_version}/streamhub-sdk.min.js"></script>
    <link rel="stylesheet" href="http://cdn.livefyre.com/libs/sdk/{sdk_version}/streamhub-sdk.min.css" />
        """.format(sdk_version=self.sdk_version)
        
        if Application_Type.WALL in self._app_types:
            header += """
    <script src="http://cdn.livefyre.com/libs/apps/Livefyre/streamhub-wall/{wall_version}/streamhub-wall.min.js"></script>
            """.format(wall_version=self.wall_version)

        return header

    def _build_body(self):
        """
        Builds body of the html file
        """

        include = ""
        if Application_Type.LIST in self._app_types:
            include += """var ListView = Livefyre.require("streamhub-sdk/content/views/content-list-view");\n\t\t\t"""
        if Application_Type.WALL in self._app_types:
            include += """var WallView = Livefyre.require("streamhub-wall");\n"""

        script = ""
        html_els = ""
        for i, app in enumerate(self._apps):
            opt_template, opt_var = app.build_opts_fragment(i)
            view_template, view_var, view_el = app.build_view_fragment(i)
            col_template, col_var = app.build_collection_fragment(i, opt_var, view_var)
            html_els += "<div id='{}'></div>".format(view_el)
            script += opt_template + view_template + col_template

        body = """
    {html_els}
    <script>
        (function () {{
            var Collection = Livefyre.require("streamhub-sdk/collection");
            {include}
            {script}
        }})();
    </script>
        """.format(html_els=html_els, include=include, script=script)

        return body

    def generate_html(self):
        header = self._build_header()
        body = self._build_body()

        template = """
<!DOCTYPE html>
<html>
<head>
    {header}
</head>
<body>
    {body}
</body>
</html>
        """.format(header=header, body=body)

        f = open(self.filename, "w")
        f.write(template)
        f.close()
        print "\nSuccess. File can be found here {}\n".format(self.filename)

def get_versions(args_dict):
    """
    Modifies the args dict based upon the options it has to get the appropriate sdk and application
    versions.
    """

    if args_dict["wall_article_ids"] and (not args_dict["wall_version"] or not args_dict["sdk_version"]):
        print "ERROR: Must specify both wall version and sdk version if specifying a wall version"
        sys.exit(2)

    if args_dict["wall_article_ids"] and not args_dict["wall_version"] and not args_dict["sdk_version"]:
        url = "http://appgallery.herokuapp.com/api/v1/packages/json"
        apps = json.loads(urllib2.urlopen(url).read())
        for app in apps:
            if app["id"] == "Livefyre/streamhub-wall":
                args_dict["wall_version"] = app["latestBuild"].get("version", "")
                args_dict["sdk_version"] = app["latestBuild"].get("sdkVersion", "")
                break

    if args_dict["list_article_ids"] and not args_dict["sdk_version"]:
        reg = re.compile("^v\d+\.\d+\.\d+$")
        url = "https://api.github.com/repos/Livefyre/streamhub-sdk/tags"
        tags =  json.loads(urllib2.urlopen(url).read())
        for tag in tags:
            if reg.match(tag["name"]):
                args_dict["sdk_version"] = tag["name"]
                break

def main():
    """
    The main entry point to the application
    """

    # Parse the command options
    parser = argparse.ArgumentParser(description="A way to generate boilerplate code for media walls and list feeds")
    parser.add_argument("-n", "--network", help="the network the app is for (e.g. example.fyre.co)", required=True)
    parser.add_argument("-s", "--site-id", help="the site id the app is for (e.g. 123456)", required=True)

    parser.add_argument("--wall-article-ids", nargs="+", help="article ids for media walls (e.g. article-id-1 article-id-2")
    parser.add_argument("--list-article-ids", nargs="+", help="article ids for list views (e.g. article-id-1 article-id-2")

    parser.add_argument("-f", "--filename", help="the output filename", default="./index.html")
    parser.add_argument("-v", "--sdk-version", help="(optional - will attempt to use latest) which sdk version you'd like to use")
    parser.add_argument("-w", "--wall-version", help="(optional - will attempt to use latest) which version of the media wall you want to use")

    args = parser.parse_args()
    args_dict = vars(args)
    if not args_dict["list_article_ids"] and not args_dict["wall_article_ids"]:
        print "ERROR: Must have at least 1 list_article_ids or wall_article_ids"
        sys.exit(2)

    get_versions(args_dict)

    generator = Generator(**args_dict)
    generator.generate_html()

if __name__ == "__main__":
    main()

