$(() => {
    const filter_form = $("#filter_form").first();
    if (filter_form) {
        $("#filter_form input[type=reset]").on("click", (e) => {
            e.preventDefault();
            $("#filter_form input[type=text]").val("");
            $("#filter_form select").children().prop("selected", false);
            $("#filter_form input[type=date]").val("");
        });
    }
});
