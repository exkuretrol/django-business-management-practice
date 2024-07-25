$(() => {
    const is_no_end_date_label = $("label[for=checkbox-id-is_no_end_date]");

    is_no_end_date_label.text("沒有結束日期");

    const is_no_end_date = $("#checkbox-id-is_no_end_date");
    end_date_el = document.getElementById("id_effective_end_date");
    let end_date_picker = new Litepicker({
        element: end_date_el,
    });

    end_date_picker.setDate("9999-12-31");
    $(end_date_el).attr("readonly", true);

    is_no_end_date.on("change", (e, el, data) => {
        set_end_picker(e.target);
    });

    function set_end_picker(el) {
        if ($(el).is(":checked")) {
            end_date_picker.setDate("9999-12-31");
            $(end_date_el).attr("readonly", true);
        } else {
            end_date_picker.setDate(
                new Date().getTime() + 30 * 24 * 60 * 60 * 1000
            );
            $(end_date_el).attr("readonly", false);
        }
    }
});
