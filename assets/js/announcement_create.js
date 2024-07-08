$(() => {
    const form = $(".content__wrap form").first();
    const tags = Tags.getInstance(document.getElementById("id_branchs"));
    const quill = Quill.find(document.getElementById("quill-id_content"));

    if (form) {
        form.find("input[type=reset]").on("click", (e) => {
            e.preventDefault();
            if (quill) {
                quill.setText("");
            }

            $("#filter_form input[type=text]").val("");
            $("#filter_form input[type=date]").val("");
            tags.removeAll();
        });
    }
});
