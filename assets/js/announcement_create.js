const toolbarOptions = [
    [{ header: [1, 2, 3, false] }],
    ["bold", "italic", "underline"], // toggled buttons
    [{ indent: "-1" }, { indent: "+1" }], // outdent/indent
    [{ align: "" }, { align: "center" }, { align: "right" }], // text align
    ["link"],
    [{ list: "ordered" }, { list: "bullet" }, { list: "check" }],
    ["clean"], // remove formatting button
];

$(() => {
    const quill = new Quill("#editor", {
        theme: "snow",
        modules: {
            toolbar: toolbarOptions,
        },
    });
});
