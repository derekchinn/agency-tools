import string, os, argparse
from HTMLParser import HTMLParser

class HTML_File_Builder_Operations (object):
    REPLACE_WITH = "replace-with"

class HTML_File_Builder(HTMLParser):
    def __init__(self, in_file, out_file="./index.html"):
        HTMLParser.__init__(self)
        self.inCommentBlock = False
        self.exitedCommentBlock = False
        self.cur_op = ""
        self.op_stack = []
        self.type_stack = []
        self.resource_stack = []
        self.in_file = in_file
        self.out_file = open(out_file, "w")
        self.last_raw_data = ""

    def handle_comment(self, data):
        """
        Process the comment
        """

        comment = string.lower(string.strip(data))
        split_comment = string.split(comment)

        # Do we have the literal "end" in the comment and is the last operation on the stack
        # the same as the the one that started this?
        if split_comment[0] == "end" and self.op_stack[len(self.op_stack) - 1] in split_comment:
            self.exitedCommentBlock = True
            return

        # Is this comment even a command?
        split_command = string.split(comment, ":")
        if split_command[0] in (HTML_File_Builder_Operations.REPLACE_WITH):
            self.inCommentBlock = True

            # Put operations on stack
            self.op_stack.append(split_command[0])
            self.type_stack.append(split_command[1])
            self.resource_stack.append(split_command[2])
            return

        # Otherwise, just write this business out since it's a real comment.
        self._write_to_file(self.rawdata)

    def handle_data(self, data):
        """
        Write Data to the file if the right conditions are met.
        """

        if self.inCommentBlock:
            if self.exitedCommentBlock:
                self.cur_op = self.op_stack.pop()
                type = self.type_stack.pop()
                resource = self.resource_stack.pop()

                if type == "js":
                    if self.cur_op == HTML_File_Builder_Operations.REPLACE_WITH:
                        data = "<script src='{resource}'></script>\n".format(resource=resource)

                if type == "css":
                    if self.cur_op == HTML_File_Builder_Operations.REPLACE_WITH:
                        data = "<link rel='stylesheet' href='{resource}' />\n".format(resource=resource)

                self.exitedCommentBlock = False

                # Arbitrarily picked the op stack.. should
                # have the same length as all the other stacks, though. Anyways,
                # this allows for nested comment blocks...
                if len(self.op_stack) == 0:
                    self.inCommentBlock = False

            self._write_to_file(data)

    def handle_starttag(self, tag, attrs):
        self._write_to_file(self.rawdata)

    def handle_endtag(self, tag):
        self._write_to_file(self.rawdata)

    def handle_decl(self, decl):
        self._write_to_file(self.rawdata)

    def _write_to_file(self, data):
        """
        Handles writing the line out to the file for the non-data
        data lines between the comment blocks.
        """

        # Ignore stuff between comment blocks if we're doing the replace-with
        # command or if the string we're processing is the same as the last one
        # we just did. This is necessary because you can have a open tag and
        # close tag on the same line, which causes the print command to be
        # fired off twice for the same line.
           
        if data != "\n" and not self.inCommentBlock and self.rawdata != self.last_raw_data: 
            self.last_raw_data = self.rawdata
            self.out_file.write(data)

    def run(self):
        """
        Run the html parser
        """

        r = open(self.in_file, "r")
        for line in r:
            self.feed(line)
        r.close()
        self.out_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in-file", required=True)
    parser.add_argument("-o", "--out-file", required=True)
    args = parser.parse_args()
    args_dict = vars(args)

    builder = HTML_File_Builder(**args_dict)
    builder.run()
    builder.close()
main()
