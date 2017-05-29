import sublime
import sublime_plugin

def to_first_non_tab_on_line(view, pt):
    while True:
        c = view.substr(pt)
        if c == "\t":
            pt += 1
        else:
            break

    return pt

def to_next_non_white_space_on_line(view, pt):
    while True:
        c = view.substr(pt)
        if c == " ":
            pt += 1
        else:
            break

    return pt

def to_prev_separator_on_line(view, pt, follow):
    while True:
        c = view.substr(pt)
        if c in follow:
            if not (c==" " and view.substr(pt-1)=="\t"):
                pt += 1
            break
        else:
            pt -= 1

    return pt

class ColAlignCommand(sublime_plugin.TextCommand):

    def run(self, edit, follow="\n\t ,([{:;"):
        view = self.view
        origin = []
        maxcol = 0
        maxori = 0
        second = -1
        for region in view.sel():
            lines = view.lines(region)
            if len(lines)!=1:
                view.run_command('indent')
                continue

            pos = 0

            if view.substr(region.a) == " ":
                pos = to_next_non_white_space_on_line(view, region.a)
            else:
                pos = to_prev_separator_on_line(view, region.a - 1, follow)

            tab = view.rowcol(to_first_non_tab_on_line(
                    view, lines[0].begin()
                ))[1]

            offset = view.rowcol(pos)[1] + tab*3
            origin.append((pos, offset, offset == tab*4))
            col = offset + 4 - offset % 4

            if maxcol < col:
                if maxori: second = maxori
                maxcol = col
                maxori = offset
            elif second < offset:
                second = offset

        origin.sort()
        offset = 0
        prev = -1

        if len(origin)!=1 and second!=-1 and \
            maxori > second and (maxcol-maxori) % 4 == 0:
            maxcol = maxori

        for (pos, col, eq) in origin:
            if prev == pos or \
                maxori == col and maxcol == col: continue
            prev = pos #unique

            if eq:
                col = (maxcol-col) // 4
                view.insert(edit, pos+offset, "\t" * col)
            else:
                col = maxcol-col
                view.insert(edit, pos+offset, " " * col)

            offset+=col

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

