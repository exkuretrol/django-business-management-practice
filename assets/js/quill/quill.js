const Link = Quill.import("formats/link");
const Toolbar = Quill.import("modules/toolbar");
const Snow = Quill.import("themes/snow");
const Bold = Quill.import("formats/bold");
const Italic = Quill.import("formats/italic");
const Underline = Quill.import("formats/underline");

class MyLink extends Link {
    static PROTOCOL_WHITELIST = ["http", "https"];
    static create(value) {
        const node = Link.create(value);
        value = MyLink.sanitize(value);
        node.setAttribute("href", value);
        node.removeAttribute("target");
        return node;
    }

    static sanitize(url) {
        // make sure the link add "https://" if it doesn't have protocol
        if (url.indexOf(":") == -1) {
            url = "https://" + url;
        }
        return super.sanitize(url);
    }

    format(name, value) {
        super.format(name, value);
        this["domNode"].removeAttribute("target");
    }
}

Quill.register(
    {
        "modules/toolbar": Toolbar,
        "themes/snow": Snow,
        "formats/bold": Bold,
        "formats/italic": Italic,
        "formats/underline": Underline,
        "formats/link": MyLink,
    },
    // suppress log
    true
);

Quill.debug("error");
