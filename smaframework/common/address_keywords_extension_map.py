import re

'''
 * Parses an address string to collect the relevant keywords.
 *
 * @param address - The address string.
 * @param mode - `extend` (to add abbreviations) or `clean` (to remove commom words).
'''
def parse_str(address, mode='clean'):
    address_str = re.sub('[^a-zA-Z0-9\-]+', ' ', address).lower()
    address_keywords = address_str.split()
    
    if mode == 'extend':
        extensions = list(map(lambda k: next((tp for tp in address_keywords_extensions if k in tp), []), address_keywords))
        for e in extensions:
            if len(e):
                address_keywords.extend(e)
    elif mode == 'clean':
        address_keywords = [item for item in address_keywords if item not in address_stop_words]
    return address_keywords

address_stop_words = ["alley","allee","aly","ally","anex","anx","annex","annx","arcade","arc","avenue","av","ave","aven","avenu","avn","avnue","bayou","bayoo","byu","beach","bch","bend","bnd","bluff","blf","bluf","bluffs","blfs","bottom","bot","btm","bottm","boulevard","blvd","boul","boulv","branch","br","brnch","bridge","brdge","brg","brook","brk","brooks","brks","burg","bg","burgs","bgs","bypass","byp","bypa","bypas","byps","camp","cp","cmp","canyon","canyn","cyn","cnyn","cape","cpe","causeway","cswy","causwa","center","cen","ctr","cent","centr","centre","cnter","cntr","centers","ctrs","circle","cir","circ","circl","crcl","crcle","circles","cirs","cliff","clf","cliffs","clfs","club","clb","common","cmn","commons","cmns","corner","cor","corners","cors","course","crse","court","ct","courts","cts","cove","cv","coves","cvs","creek","crk","crescent","cres","crsent","crsnt","crest","crst","crossing","xing","crssng","crossroad","xrd","crossroads","xrds","curve","curv","dale","dl","dam","dm","divide","div","dv","dvd","drive","dr","driv","drv","drives","drs","estate","est","estates","ests","expressway","exp","expy","expr","express","expw","extension","ext","extn","extnsn","extensions","exts","fall","falls","fls","ferry","fry","frry","field","fld","fields","flds","flat","flt","flats","flts","ford","frd","fords","frds","forest","frst","forests","forge","forg","frg","forges","frgs","fork","frk","forks","frks","fort","ft","frt","freeway","fwy","freewy","frway","frwy","garden","gdn","gardn","grden","grdn","gardens","gdns","grdns","gateway","gtwy","gatewy","gatway","gtway","glen","gln","glens","glns","green","grn","greens","grns","grove","grov","grv","groves","grvs","harbor","harb","hbr","harbr","hrbor","harbors","hbrs","haven","hvn","heights","ht","hts","highway","hwy","highwy","hiway","hiwy","hway","hill","hl","hills","hls","hollow","hllw","holw","hollows","holws","inlet","inlt","island","is","islnd","islands","iss","islnds","isle","isles","junction","jct","jction","jctn","junctn","juncton","junctions","jctns","jcts","key","ky","keys","kys","knoll","knl","knol","knolls","knls","lake","lk","lakes","lks","land","landing","lndg","lndng","lane","ln","light","lgt","lights","lgts","loaf","lf","lock","lck","locks","lcks","lodge","ldg","ldge","lodg","loop","loops","mall","manor","mnr","manors","mnrs","meadow","mdw","meadows","mdw","mdws","medows","mews","mill","ml","mills","mls","mission","missn","msn","mssn","motorway","mtwy","mount","mnt","mt","mountain","mntain","mtn","mntn","mountin","mtin","mountains","mntns","mtns","neck","nck","orchard","orch","orchrd","oval","ovl","overpass","opas","park","prk","parks","park","parkway","pkwy","parkwy","pkway","pky","parkways","pkwy","pkwys","pass","passage","psge","path","paths","pike","pikes","pine","pne","pines","pnes","place","pl","plain","pln","plains","plns","plaza","plz","plza","point","pt","points","pts","port","prt","ports","prts","prairie","pr","prr","radial","rad","radl","radiel","ramp","ranch","rnch","ranches","rnchs","rapid","rpd","rapids","rpds","rest","rst","ridge","rdg","rdge","ridges","rdgs","river","riv","rvr","rivr","road","rd","roads","rds","route","rte","row","rue","run","shoal","shl","shoals","shls","shore","shoar","shr","shores","shoars","shrs","skyway","skwy","spring","spg","spng","sprng","springs","spgs","spngs","sprngs","spur","spurs","spur","square","sq","sqr","sqre","squ","squares","sqrs","sqs","station","sta","statn","stn","stravenue","stra","strav","straven","stravn","strvn","strvnue","stream","strm","streme","street","st","strt","str","streets","sts","summit","smt","sumit","sumitt","terrace","ter","terr","throughway","trwy","trace","trce","traces","track","trak","tracks","trk","trks","trafficway","trfy","trail","trl","trails","trls","trailer","trlr","trlrs","tunnel","tunel","tunl","tunls","tunnels","tunnl","turnpike","trnpk","tpke","turnpk","underpass","upas","union","un","unions","uns","valley","vly","vally","vlly","valleys","vlys","viaduct","vdct","via","viadct","view","vw","views","vws","village","vill","vlg","villag","villg","villiage","villages","vlgs","ville","vl","vista","vis","vist","vst","vsta","walk","walks","walk","wall","way","wy","ways","well","wl","wells","wls"]

'''
 * Map to extend addresses keywords, extracted from USPS.com Postal Explorer: C1 Street Suffix Abbreviations
 *
 * @param key - The key to retrieve extension options
'''
address_keywords_extensions = [
        [
            "alley",
            "allee",
            "aly",
            "ally"
        ],
        [
            "anex",
            "anx",
            "annex",
            "annx"
        ],
        [
            "arcade",
            "arc"
        ],
        [
            "avenue",
            "av",
            "ave",
            "aven",
            "avenu",
            "avn",
            "avnue"
        ],
        [
            "bayou",
            "bayoo",
            "byu"
        ],
        [
            "beach",
            "bch"
        ],
        [
            "bend",
            "bnd"
        ],
        [
            "bluff",
            "blf",
            "bluf"
        ],
        [
            "bluffs",
            "blfs"
        ],
        [
            "bottom",
            "bot",
            "btm",
            "bottm"
        ],
        [
            "boulevard",
            "blvd",
            "boul",
            "boulv"
        ],
        [
            "branch",
            "br",
            "brnch"
        ],
        [
            "bridge",
            "brdge",
            "brg"
        ],
        [
            "brook",
            "brk"
        ],
        [
            "brooks",
            "brks"
        ],
        [
            "burg",
            "bg"
        ],
        [
            "burgs",
            "bgs"
        ],
        [
            "bypass",
            "byp",
            "bypa",
            "bypas",
            "byps"
        ],
        [
            "camp",
            "cp",
            "cmp"
        ],
        [
            "canyon",
            "canyn",
            "cyn",
            "cnyn"
        ],
        [
            "cape",
            "cpe"
        ],
        [
            "causeway",
            "cswy",
            "causwa"
        ],
        [
            "center",
            "cen",
            "ctr",
            "cent",
            "centr",
            "centre",
            "cnter",
            "cntr"
        ],
        [
            "centers",
            "ctrs"
        ],
        [
            "circle",
            "cir",
            "circ",
            "circl",
            "crcl",
            "crcle"
        ],
        [
            "circles",
            "cirs"
        ],
        [
            "cliff",
            "clf"
        ],
        [
            "cliffs",
            "clfs"
        ],
        [
            "club",
            "clb"
        ],
        [
            "common",
            "cmn"
        ],
        [
            "commons",
            "cmns"
        ],
        [
            "corner",
            "cor"
        ],
        [
            "corners",
            "cors"
        ],
        [
            "course",
            "crse"
        ],
        [
            "court",
            "ct"
        ],
        [
            "courts",
            "cts"
        ],
        [
            "cove",
            "cv"
        ],
        [
            "coves",
            "cvs"
        ],
        [
            "creek",
            "crk"
        ],
        [
            "crescent",
            "cres",
            "crsent",
            "crsnt"
        ],
        [
            "crest",
            "crst"
        ],
        [
            "crossing",
            "xing",
            "crssng"
        ],
        [
            "crossroad",
            "xrd"
        ],
        [
            "crossroads",
            "xrds"
        ],
        [
            "curve",
            "curv"
        ],
        [
            "dale",
            "dl"
        ],
        [
            "dam",
            "dm"
        ],
        [
            "divide",
            "div",
            "dv",
            "dvd"
        ],
        [
            "drive",
            "dr",
            "driv",
            "drv"
        ],
        [
            "drives",
            "drs"
        ],
        [
            "estate",
            "est"
        ],
        [
            "estates",
            "ests"
        ],
        [
            "expressway",
            "exp",
            "expy",
            "expr",
            "express",
            "expw"
        ],
        [
            "extension",
            "ext",
            "extn",
            "extnsn"
        ],
        [
            "extensions",
            "exts"
        ],
        [
            "fall"
        ],
        [
            "falls",
            "fls"
        ],
        [
            "ferry",
            "fry",
            "frry"
        ],
        [
            "field",
            "fld"
        ],
        [
            "fields",
            "flds"
        ],
        [
            "flat",
            "flt"
        ],
        [
            "flats",
            "flts"
        ],
        [
            "ford",
            "frd"
        ],
        [
            "fords",
            "frds"
        ],
        [
            "forest",
            "frst",
            "forests"
        ],
        [
            "forge",
            "forg",
            "frg"
        ],
        [
            "forges",
            "frgs"
        ],
        [
            "fork",
            "frk"
        ],
        [
            "forks",
            "frks"
        ],
        [
            "fort",
            "ft",
            "frt"
        ],
        [
            "freeway",
            "fwy",
            "freewy",
            "frway",
            "frwy"
        ],
        [
            "garden",
            "gdn",
            "gardn",
            "grden",
            "grdn"
        ],
        [
            "gardens",
            "gdns",
            "grdns"
        ],
        [
            "gateway",
            "gtwy",
            "gatewy",
            "gatway",
            "gtway"
        ],
        [
            "glen",
            "gln"
        ],
        [
            "glens",
            "glns"
        ],
        [
            "green",
            "grn"
        ],
        [
            "greens",
            "grns"
        ],
        [
            "grove",
            "grov",
            "grv"
        ],
        [
            "groves",
            "grvs"
        ],
        [
            "harbor",
            "harb",
            "hbr",
            "harbr",
            "hrbor"
        ],
        [
            "harbors",
            "hbrs"
        ],
        [
            "haven",
            "hvn"
        ],
        [
            "heights",
            "ht",
            "hts"
        ],
        [
            "highway",
            "hwy",
            "highwy",
            "hiway",
            "hiwy",
            "hway"
        ],
        [
            "hill",
            "hl"
        ],
        [
            "hills",
            "hls"
        ],
        [
            "hollow",
            "hllw",
            "holw",
            "hollows",
            "holws"
        ],
        [
            "inlet",
            "inlt"
        ],
        [
            "island",
            "is",
            "islnd"
        ],
        [
            "islands",
            "iss",
            "islnds"
        ],
        [
            "isle",
            "isles"
        ],
        [
            "junction",
            "jct",
            "jction",
            "jctn",
            "junctn",
            "juncton"
        ],
        [
            "junctions",
            "jctns",
            "jcts"
        ],
        [
            "key",
            "ky"
        ],
        [
            "keys",
            "kys"
        ],
        [
            "knoll",
            "knl",
            "knol"
        ],
        [
            "knolls",
            "knls"
        ],
        [
            "lake",
            "lk"
        ],
        [
            "lakes",
            "lks"
        ],
        [
            "land"
        ],
        [
            "landing",
            "lndg",
            "lndng"
        ],
        [
            "lane",
            "ln"
        ],
        [
            "light",
            "lgt"
        ],
        [
            "lights",
            "lgts"
        ],
        [
            "loaf",
            "lf"
        ],
        [
            "lock",
            "lck"
        ],
        [
            "locks",
            "lcks"
        ],
        [
            "lodge",
            "ldg",
            "ldge",
            "lodg"
        ],
        [
            "loop",
            "loops"
        ],
        [
            "mall"
        ],
        [
            "manor",
            "mnr"
        ],
        [
            "manors",
            "mnrs"
        ],
        [
            "meadow",
            "mdw"
        ],
        [
            "meadows",
            "mdw",
            "mdws",
            "medows"
        ],
        [
            "mews"
        ],
        [
            "mill",
            "ml"
        ],
        [
            "mills",
            "mls"
        ],
        [
            "mission",
            "missn",
            "msn",
            "mssn"
        ],
        [
            "motorway",
            "mtwy"
        ],
        [
            "mount",
            "mnt",
            "mt"
        ],
        [
            "mountain",
            "mntain",
            "mtn",
            "mntn",
            "mountin",
            "mtin"
        ],
        [
            "mountains",
            "mntns",
            "mtns"
        ],
        [
            "neck",
            "nck"
        ],
        [
            "orchard",
            "orch",
            "orchrd"
        ],
        [
            "oval",
            "ovl"
        ],
        [
            "overpass",
            "opas"
        ],
        [
            "park",
            "prk"
        ],
        [
            "parks",
            "park"
        ],
        [
            "parkway",
            "pkwy",
            "parkwy",
            "pkway",
            "pky"
        ],
        [
            "parkways",
            "pkwy",
            "pkwys"
        ],
        [
            "pass"
        ],
        [
            "passage",
            "psge"
        ],
        [
            "path",
            "paths"
        ],
        [
            "pike",
            "pikes"
        ],
        [
            "pine",
            "pne"
        ],
        [
            "pines",
            "pnes"
        ],
        [
            "place",
            "pl"
        ],
        [
            "plain",
            "pln"
        ],
        [
            "plains",
            "plns"
        ],
        [
            "plaza",
            "plz",
            "plza"
        ],
        [
            "point",
            "pt"
        ],
        [
            "points",
            "pts"
        ],
        [
            "port",
            "prt"
        ],
        [
            "ports",
            "prts"
        ],
        [
            "prairie",
            "pr",
            "prr"
        ],
        [
            "radial",
            "rad",
            "radl",
            "radiel"
        ],
        [
            "ramp"
        ],
        [
            "ranch",
            "rnch",
            "ranches",
            "rnchs"
        ],
        [
            "rapid",
            "rpd"
        ],
        [
            "rapids",
            "rpds"
        ],
        [
            "rest",
            "rst"
        ],
        [
            "ridge",
            "rdg",
            "rdge"
        ],
        [
            "ridges",
            "rdgs"
        ],
        [
            "river",
            "riv",
            "rvr",
            "rivr"
        ],
        [
            "road",
            "rd"
        ],
        [
            "roads",
            "rds"
        ],
        [
            "route",
            "rte"
        ],
        [
            "row"
        ],
        [
            "rue"
        ],
        [
            "run"
        ],
        [
            "shoal",
            "shl"
        ],
        [
            "shoals",
            "shls"
        ],
        [
            "shore",
            "shoar",
            "shr"
        ],
        [
            "shores",
            "shoars",
            "shrs"
        ],
        [
            "skyway",
            "skwy"
        ],
        [
            "spring",
            "spg",
            "spng",
            "sprng"
        ],
        [
            "springs",
            "spgs",
            "spngs",
            "sprngs"
        ],
        [
            "spur"
        ],
        [
            "spurs",
            "spur"
        ],
        [
            "square",
            "sq",
            "sqr",
            "sqre",
            "squ"
        ],
        [
            "squares",
            "sqrs",
            "sqs"
        ],
        [
            "station",
            "sta",
            "statn",
            "stn"
        ],
        [
            "stravenue",
            "stra",
            "strav",
            "straven",
            "stravn",
            "strvn",
            "strvnue"
        ],
        [
            "stream",
            "strm",
            "streme"
        ],
        [
            "street",
            "st",
            "strt",
            "str"
        ],
        [
            "streets",
            "sts"
        ],
        [
            "summit",
            "smt",
            "sumit",
            "sumitt"
        ],
        [
            "terrace",
            "ter",
            "terr"
        ],
        [
            "throughway",
            "trwy"
        ],
        [
            "trace",
            "trce",
            "traces"
        ],
        [
            "track",
            "trak",
            "tracks",
            "trk",
            "trks"
        ],
        [
            "trafficway",
            "trfy"
        ],
        [
            "trail",
            "trl",
            "trails",
            "trls"
        ],
        [
            "trailer",
            "trlr",
            "trlrs"
        ],
        [
            "tunnel",
            "tunel",
            "tunl",
            "tunls",
            "tunnels",
            "tunnl"
        ],
        [
            "turnpike",
            "trnpk",
            "tpke",
            "turnpk"
        ],
        [
            "underpass",
            "upas"
        ],
        [
            "union",
            "un"
        ],
        [
            "unions",
            "uns"
        ],
        [
            "valley",
            "vly",
            "vally",
            "vlly"
        ],
        [
            "valleys",
            "vlys"
        ],
        [
            "viaduct",
            "vdct",
            "via",
            "viadct"
        ],
        [
            "view",
            "vw"
        ],
        [
            "views",
            "vws"
        ],
        [
            "village",
            "vill",
            "vlg",
            "villag",
            "villg",
            "villiage"
        ],
        [
            "villages",
            "vlgs"
        ],
        [
            "ville",
            "vl"
        ],
        [
            "vista",
            "vis",
            "vist",
            "vst",
            "vsta"
        ],
        [
            "walk"
        ],
        [
            "walks",
            "walk"
        ],
        [
            "wall"
        ],
        [
            "way",
            "wy"
        ],
        [
            "ways"
        ],
        [
            "well",
            "wl"
        ],
        [
            "wells",
            "wls"
        ]
    ]