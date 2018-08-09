#!/usr/bin/env python
# -*- coding: utf-8 -*-

# special thanks to da3dsoul

version = 1  # increase with each push/edit

tagBlacklistAniDBHelpers = set([  # AniDB tags that don't help with anything
    "body and host",
    "breasts",
    "broadcast cropped to 4-3",
    "cast missing",
    "cast",
    "content indicators",
    "delayed 16-9 broadcast",
    "description missing",
    "development hell",  # :( God Eater
    "dialogue driven",  # anidb and their british spellings
    "dynamic",
    "earth",
    "elements",
    "ending",
    "ensemble cast",
    "family life",
    "fast-paced",
    "fictional world",
    "full hd version available",
    "jdrama adaptation",
    "meta tags",
    "motifs",
    "multi-anime projects",
    "noitamina",
    "origin",
    "past",
    "place",
    "present",
    "season",
    "sentai",
    "setting",
    "some weird shit goin` on",  # these are some grave accents in use...
    "storytelling",
    "tales",
    "target audience",
    "technical aspects",
    "television programme",
    "themes",
    "time",
    "translation convention",
    "tropes",
    "ungrouped",
    "unsorted"
])

tagBlackListSource = set([  # tags containing source of serie
    "4-koma",
    "action game",
    "erotic game",
    "fan-made",
    "game",
    "korean drama",
    "manga",
    "manhua",
    "manhwa",
    "movie",
    "new",
    "novel",
    "radio programme",
    "remake",
    "rpg",
    "television programme",
    "ultra jump",
    "visual novel"
])

tagBlackListArtStyle = set([  # tags that focus on art style
    "3d cg animation",
    "3d cg closing",
    "cel-shaded animation",
    "cgi",
    "chibi ed",
    "experimental animation",
    "flash animation",
    "live-action closing",
    "live-action imagery",
    "off-model animation",
    "photographic backgrounds",
    "product placement",
    "recycled animation",
    "slide show animation",
    "thick line animation",
    "vignette scenes",
    "watercolour style",
    "widescreen transition"
])

tagBlackListUsefulHelpers = set([  # tags that focus on episode attributes
    "ed variety",
    "half-length episodes",
    "long episodes",
    "multi-segment episodes",
    "op and ed sung by characters",
    "op variety",
    "post-credits scene",
    "recap in opening",
    "short episodes",
    "short movie",
    "stand-alone movie",
    "subtle op ed sequence change"
])

tagBlackListPlotSpoilers = set([  # tags that could contain story-line spoilers
    "branching story",
    "cliffhangers",
    "colour coded",
    "complex storyline",
    "drastic change in sequel",
    "fillers",
    "first girl wins",  # seriously a spoiler
    "incomplete story",
    "inconclusive",
    "inconclusive romantic plot",
    "non-linear",
    "open-ended",
    "room for sequel",
    "sudden change of pace",
    "tone changes",
    "unresolved",
    "unresolved romance"
])


def processTags(flags, string):

    """
        Filters tags based on settings specified in flags
    :param flags:
            0b00001 : Hide AniDB Internal Tags
            0b00010 : Hide Art Style Tags
            0b00100 : Hide Source Work Tags
            0b01000 : Hide Useful Miscellaneous Tags
            0b10000 : Hide Plot Spoiler Tags
    :param string: A list of strings [ 'meta tags', 'elements', 'comedy' ]
    :return: The list of strings after filtering
    """
    toRemove=set()
    removeOriginal=False

    for a in string:
        tag = str(a).lower().strip()
        if flags & 0b00010 == 0b00010:
            if tag in tagBlackListArtStyle:
                toRemove.add(a)
            if "censor" in tag:
                toRemove.add(a)
        if flags & 0b00100 == 0b00100:
            if tag in tagBlackListSource:
                toRemove.add(a)
            if "original work" == tag:
                toRemove.add(a)
        else:
            if tag in tagBlackListSource:
                removeOriginal=True

        if flags & 0b01000 == 0b01000:
            if tag in tagBlackListUsefulHelpers:
                toRemove.add(a)
            if tag.startswith("preview"):
                toRemove.add(a)

        if flags & 0b10000 == 0b10000:
            if tag in tagBlackListPlotSpoilers:
                toRemove.add(a)
            if tag.startswith("plot"):
                toRemove.add(a)
            if tag.endswith(" dies"):
                toRemove.add(a)
            if tag.endswith(" end"):
                toRemove.add(a)
            if tag.endswith(" ending"):
                toRemove.add(a)

        if flags & 0b00001 == 0b00001:
            if tag in tagBlacklistAniDBHelpers:
                toRemove.add(a)
            if "to be" in tag:
                if "merged" in tag:
                    toRemove.add(a)
                elif "deleted" in tag:
                    toRemove.add(a)
                elif "split" in tag:
                    toRemove.add(a)
                elif "moved" in tag:
                    toRemove.add(a)
                elif "improved" in tag or "improving" in tag or "improvement" in tag:
                    toRemove.add(a)
            elif "need" in tag or "needs" in tag:
                if "merging" in tag or "merged" in tag:
                    toRemove.add(a)
                elif "deleting" in tag or "deleted" in tag:
                    toRemove.add(a)
                elif "moving" in tag or "moved" in tag:
                    toRemove.add(a)
                elif "improved" in tag or "improving" in tag or "improvement" in tag:
                    toRemove.add(a)
            elif "old animetags" in tag:
                toRemove.add(a)
            elif "missing" in tag:
                toRemove.add(a)
            elif tag.startswith("predominantly"):
                toRemove.add(a)
            elif tag.startswith("weekly"):
                toRemove.add(a)

    toAdd = []
    # on a separate loop in case 'original work' came before the source
    if removeOriginal:
        for a in string:
            tag = str(a).lower().strip()
            if tag == "new":
                toAdd.append('Original Work')
            elif tag == "original work":
                toRemove.add("original work")
                # both just in case
                toRemove.add("Original Work")
                break

    for a in toRemove:
        if a in string:
            string.remove(a)

    for a in toAdd:
        if a not in string:
            string.append(a)

    return string
