$(() => {
    const form = $(".content__wrap form").first();
    const tags = Tags.getInstance(document.getElementById("id_branchs"));
    const quill = Quill.find(document.getElementById("quill-id_content"));
    const is_no_end_date_label = $("label[for=checkbox-id-is_no_end_date]");

    is_no_end_date_label.text("沒有結束日期");

    const is_no_end_date = $("#checkbox-id-is_no_end_date");

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

    const formset = $(".formset");
    const prefix = "Announcement_attachments";
    const total_forms = $("#id_" + prefix + "-TOTAL_FORMS").prop(
        "autocomplete",
        "off"
    );
    let next_index = parseInt(total_forms.val(), 10);
    const max_forms = $("#id_" + prefix + "-MAX_NUM_FORMS").prop(
        "autocomplete",
        "off"
    );
    const min_forms = $("#id_" + prefix + "-MIN_NUM_FORMS").prop(
        "autocomplete",
        "off"
    );
    let add_button;

    const update_element_index = (el, prefix, idx) => {
        const id_regex = new RegExp(prefix + "-(\\d+|__prefix__)");
        const replacement = prefix + "-" + idx;

        if ($(el).prop("for"))
            $(el).prop("for", $(el).prop("for").replace(id_regex, replacement));
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    };

    const add_inline_add_button = () => {
        if (add_button == null) {
            total_forms
                .parent()
                .append(
                    "<button type='button' class='btn btn-primary' id='add_attachment'>新增附件</button>"
                );
            add_button = $("#add_attachment");
        }
        add_button.on("click", add_inline_click_handler);
    };

    const add_inline_click_handler = (e) => {
        e.preventDefault();
        const template = $("#" + prefix + "-empty");
        const row = template.clone(true);
        row.attr("id", prefix + "-" + next_index);
        row.children(":first").removeAttr("id");
        row.removeClass("d-none");
        add_inline_delete_button(row);
        row.find("*").each((i, el) => {
            update_element_index(el, prefix, next_index);
        });
        row.insertBefore($(template));
        $(total_forms).val(parseInt(total_forms.val(), 10) + 1);
        next_index++;
        if (max_forms.val() != "" && max_forms.val() - total_forms.val() <= 0) {
            add_button.hide();
        }
    };

    add_inline_add_button();

    const add_inline_delete_button = (row) => {
        let delete_button_location;
        if (row.children(":last").hasClass("row"))
            delete_button_location = row.children(":last").children(":last");
        else delete_button_location = row.children(":last");
        delete_button_location.append(
            '<button class="btn btn-icon btn-xs btn-danger rounded-circle"><i class="psi-trash"></i></button>'
        );
        row.find("button.btn-danger").on(
            "click",
            inline_delete_handler.bind(this)
        );
    };

    const inline_delete_handler = (e) => {
        e.preventDefault();
        const delete_button = $(e.target);
        const row = delete_button.closest(
            "div[id^=Announcement_attachments]:not(.d-none)"
        );
        const inline_group = row.closest(".formset");
        row.remove();
        next_index--;
        const forms = inline_group
            .children()
            .filter("div[id^=Announcement_attachments]:not(.d-none)");
        total_forms.val(forms.length);
        if (max_forms.val() != "" && max_forms.val() - forms.length > 0) {
            add_button.show();
        }
        let i, form_count;
        const update_element_callback = (el) => {
            update_element_index(el, prefix, i);
        };
        for (i = 0, form_count = forms.length; i < forms.length; i++) {
            update_element_index(forms.get(i), prefix, i);
            $(forms.get(i))
                .find("*")
                .each((i, el) => update_element_callback(el));
        }
    };

    formset
        .children()
        .filter("div[id^=Announcement_attachments]:not(.d-none)")
        .each((i, el) => {
            const row = $(el);
            add_inline_delete_button(row);
        });
    // TODO: fix duplicated id
});
