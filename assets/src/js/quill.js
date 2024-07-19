import Quill from "quill/core";

import Toolbar from "quill/modules/toolbar";
import Snow from "quill/themes/snow";

import Bold from "quill/formats/bold";
import Italic from "quill/formats/italic";
import Underline from "quill/formats/underline";
import Link from "quill/formats/link";
class MyLink extends Link {
    static create(value) {
        const node = Link.create(value);
        value = Link.sanitize(value);
        node.setAttribute("href", value);
        node.removeAttribute("target");
        return node;
    }

    format(name, value) {
        super.format(name, value);
        this["domNode"].removeAttribute("target");
    }
}

Quill.register({
    "modules/toolbar": Toolbar,
    "themes/snow": Snow,
    "formats/bold": Bold,
    "formats/italic": Italic,
    "formats/underline": Underline,
    "formats/link": MyLink,
});

export default Quill;