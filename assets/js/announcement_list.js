const data = document.currentScript.dataset;

$(() => {
    const form = $(".content__wrap form").first();
    const tags = Tags.getInstance(document.getElementById("id_branchs"));

    if (form) {
        form.find("input[type=reset]").on("click", (e) => {
            e.preventDefault();

            $("#filter_form input[type=text]").val("");
            $("#filter_form input[type=date]").val("");
            tags.removeAll();
        });
    }

    const check_all = $("#check_all").first();
    check_all.on("click", () => {
        $("tbody tr input[type=checkbox]").prop(
            "checked",
            check_all.prop("checked")
        );
    });

    const btn_archive = $("#btn_archive").first();
    const btn_publish = $("#btn_publish").first();
    const btn_unpublish = $("#btn_unpublish").first();
    $([btn_archive, btn_publish, btn_unpublish]).each((i, btn) => {
        btn.on("click", (_, el) => {
            let action;
            if (btn === btn_archive) {
                action = "archive";
            } else if (btn === btn_publish) {
                action = "publish";
            } else if (btn === btn_unpublish) {
                action = "unpublish";
            }
            const selected = $("tbody tr input[type=checkbox]:checked");
            if (selected.length > 0) {
                const ids = selected
                    .map((_, el) => $(el).closest("tr").data("id"))
                    .get();

                $.ajax({
                    url: data.announcementActionUrl,
                    method: "POST",
                    data: JSON.stringify({
                        announcements: ids,
                        action: action,
                    }),
                    dataTyle: "json",
                    contentType: "application/json",
                }).done(() => {
                    location.reload();
                });
            }
        });
    });
});
