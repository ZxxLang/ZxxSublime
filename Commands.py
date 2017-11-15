import sublime
import sublime_plugin
import unicodedata

def to_first_non_tab_on_line(view, pt):
    while True:
        c = view.substr(pt)
        if c != "\t":
            break
        pt += 1
    return pt

def visual_width(view, pt, tabsize):
    width = 0
    while pt>0 and view.rowcol(pt)[1]>0:
        pt -= 1
        c = view.substr(pt)
        if c == "\t":
            width += tabsize
        elif ord(c) < 255:
            width += 1
        else:
            c = unicodedata.east_asian_width(c)
            width += (c == "W" or c == "F") and 2 or 1

    return width

class ColAlignCommand(sublime_plugin.TextCommand):

    def run(self, edit, follow="\n\t ,([{:"):
        view = self.view
        origin = []
        maxwidth = 0
        offset = 0
        tabSize = view.settings().get('tab_size')
        regions = view.sel()
        for region in view.sel():
            lines = view.lines(region)
            if len(lines)!=1:
                view.run_command("indent")
                continue

            pos = region.begin()

            while view.substr(pos) == " ": pos+=1

            while pos > 0:
                if view.substr(pos - 1) in follow:
                    break
                pos -= 1

            col = view.rowcol(pos)[1]
            if col == 0 or view.substr(pos-1)=="\t":
                origin.append((pos, -1))
                continue

            width = visual_width(view, pos, tabSize)


            origin.append((pos, width))
            if maxwidth < width:
                maxwidth = width + width % 2

        origin.sort()

        count = 0
        for (pos, width) in origin:
            if(width == -1):
                view.insert(edit, pos+offset, "\t")
                offset+=1
                continue

            width = maxwidth - width
            if width>0:
                view.insert(edit, pos+offset, " " * width)
                count+=1
                offset+=width

        if count == 0:
            for (pos, width) in origin:
                if(width != -1):
                    view.insert(edit, pos+offset, "  ")
                    offset+=1


class ToggleRuneCommentCommand(sublime_plugin.TextCommand):

    def run(self, edit, rune=" "):

        view = self.view

        for region in view.sel():

            start_positions = [r.begin() for r in view.lines(region)]
            start_positions.reverse()

            for pos in start_positions:
                pos = to_first_non_tab_on_line(view, pos)

                if view.substr(pos) == "\n":
                    continue

                if view.substr(pos) == rune:
                    view.erase(edit, sublime.Region(pos, pos + 1))
                else:
                    view.insert(edit, pos, rune)

