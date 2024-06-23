import Quill from "quill/core";

import Toolbar from "quill/modules/toolbar";
import Snow from "quill/themes/snow";

import Bold from "quill/formats/bold";
import Italic from "quill/formats/italic";
import Header from "quill/formats/header";
import Underline from "quill/formats/underline";
import List from "quill/formats/list";
import Link from "quill/formats/link";
import { AlignClass } from "quill/formats/align";
import Indent from "quill/formats/indent";

Quill.register({
    "modules/toolbar": Toolbar,
    "themes/snow": Snow,
    "formats/bold": Bold,
    "formats/italic": Italic,
    "formats/header": Header,
    "formats/underline": Underline,
    "formats/list": List,
    "formats/link": Link,
    "formats/align": AlignClass,
    "formats/indent": Indent,
});

export default Quill;
