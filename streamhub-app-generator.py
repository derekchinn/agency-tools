import sys, itertools, os, argparse

class Application_Type(object):
    LIST = "list"
    WALL = "wall"

class App_Generator(object):
    def __init__(self, app_type, network, site_id, article_ids, sdk_version, wall_version, filename="index.html"):
        self.app_type = self._get_app_type(app_type)
        self.filename = filename
        self.sdk_version = sdk_version
        self.wall_version = wall_version
        self.network = network
        self.site_id = site_id
        self.article_ids = list(itertools.imap(lambda x: x.strip(), article_ids))

    def _get_app_type(self, app_type):
        """
        Figure out what app type we're making here
        """

        if not app_type:
            print "Error, no application type provided"
            sys.exit(2)

        if app_type == "list":
            return Application_Type.LIST

        if app_type == "wall":
            return Application_Type.WALL

    def _build_view(self, var_id):
        """
        Builds the JS for the view
        """

        view_type_cc = ""
        view_type = ""
        el_prefix = ""

        if self.app_type == Application_Type.LIST:
            view_type_cc = "listView"
            view_type = "ListView"
            el_prefix = "list"
        else:
            view_type_cc = "wallView"
            view_type = "WallView"
            el_prefix = "wall"

        template = """
            var {view_type_cc}{iter} = new {view_type}({{
                initial: 10,
                showMore: 2,
                el: document.getElementById("{el_prefix}-{iter}")
            }});
        """.format(view_type_cc=view_type_cc, view_type=view_type, iter=var_id, el_prefix=el_prefix)

        return template, "{}{}".format(view_type_cc, var_id), "{}-{}".format(el_prefix, var_id)

    def _build_opts(self, var_id, article_id):
        """
        Build the opts for each application
        """

        template = """
            var opt{iter} = {{
                network: '{network}',
                siteId: '{site_id}',
                articleId: '{article_id}'
            }};
        """.format(iter=var_id, network=self.network, site_id=self.site_id, article_id=article_id)

        return template, "opt{}".format(var_id)

    def _build_collection(self, var_id, opt_var, view_var, view_el):
        """
        Build the final js for connecting the collection with the view.
        """

        template = """
            var collection{iter} = new Collection({opt_var});
            collection{iter}.pipe({view_var});
        """.format(iter=var_id, opt_var=opt_var, view_var=view_var)

        return template, "collection{}".format(var_id)

    def build_body(self):
        include = ""
        if self.app_type == Application_Type.LIST:
            include += """var ListView = Livefyre.require("streamhub-sdk/content/views/content-list-view");"""
        if self.app_type == Application_Type.WALL:
            include += """var WallView = Livefyre.require("streamhub-wall");"""

        script = ""
        html_els = ""
        for i, article_id in enumerate(self.article_ids):
            opt_template, opt_var = self._build_opts(i, article_id)
            view_template, view_var, view_el = self._build_view(i)
            col_template, col_var = self._build_collection(i, opt_var, view_var, view_el)
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

    def build_header(self):
        """
        Builds the header section for the html file
        """

        header = """
    <script src="http://cdn.livefyre.com/libs/sdk/{sdk_version}/streamhub-sdk.min.js"></script>
    <link rel="stylesheet" href="http://cdn.livefyre.com/libs/sdk/{sdk_version}/streamhub-sdk.min.css" />
        """.format(sdk_version=self.sdk_version)
        
        if self.app_type == Application_Type.WALL:
            header += """
    <script src="http://cdn.livefyre.com/libs/apps/Livefyre/streamhub-wall/{wall_version}/streamhub-wall.min.js"></script>
            """.format(wall_version=self.wall_version)

        return header

    def generate_html(self):
        header = self.build_header()
        body = self.build_body()

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

def main():
    """
    The main entry point to the application
    """

    # Parse the command options
    parser = argparse.ArgumentParser(description="A way to generate boilerplate code for media walls and list feeds")
    parser.add_argument("-n", "--network", help="the network the app is for (e.g. example.fyre.co)", required=True)
    parser.add_argument("-s", "--site-id", help="the site id the app is for (e.g. 123456)", required=True)
    parser.add_argument("-a", "--article-ids", nargs="+", help="article ids of the collections (e.g. article-id-1 article-id-2 article-id-3", required=True)
    parser.add_argument("-t", "--app-type", help="the type of app to be generated (current options are only list and wall)", required=True)
    parser.add_argument("-f", "--filename", help="the output filename", default="index.html")
    parser.add_argument("-v", "--sdk-version", help="(optional - will attempt to use latest) which sdk version you'd like to use", default="v2.6.1")
    parser.add_argument("-w", "--wall-version", help="(optional - will attempt to use latest) which version of the medi wall you want to use", default="v2.2.4-build.155")

    args = parser.parse_args()
    generator = App_Generator(**vars(args))
    generator.generate_html()

if __name__ == "__main__":
    main()

