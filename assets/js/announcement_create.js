const dataset = document.currentScript.dataset;

$(() => {
    const form = $(".content__wrap form").first();
    const branchs_tag = Tags.getInstance(document.getElementById("id_branchs"));
    const quill = Quill.find(document.getElementById("quill-id_content"));
    const is_no_end_date_label = $("label[for=checkbox-id-is_no_end_date]");
    const announcement_status = $("input[name=status]");
    const draft_button = form.find("input[name=draft]");
    const publish_button = form.find("input[name=publish]");

    is_no_end_date_label.text("沒有結束日期");

    const is_no_end_date = $("#checkbox-id-is_no_end_date");

    form.find("input[type=reset]").on("click", (e) => {
        e.preventDefault();
        if (quill) {
            quill.setText("");
        }

        form.find("input[name=title]").val("");
        branchs_tag.removeAll();
    });

    let attachments_to_delete = [];

    const form_submit_handler = (form) => {
        if (attachments_to_delete.length > 0) {
            max_forms.val(
                parseInt(max_forms.val()) + attachments_to_delete.length
            );
            total_forms.val(
                parseInt(total_forms.val()) + attachments_to_delete.length
            );
            formset
                .find("tr[id^=Announcement_attachments]:not(.d-none)")
                .each((i, el) => {
                    if ($(el).find("select").val() == "") {
                        $(el).remove();
                        next_index--;
                        total_forms.val(total_forms.val() - 1);
                    }
                });

            const forms = get_attachment_rows(false);
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

            for (let i = 0; i < attachments_to_delete.length; i++) {
                formset.append(
                    $("<input>", {
                        name: prefix + "-" + next_index + "-id",
                        value: attachments_to_delete[i].id,
                        type: "hidden",
                    })
                );
                formset.append(
                    $("<input>", {
                        name: prefix + "-" + next_index + "-file",
                        value: attachments_to_delete[i].file,
                        type: "hidden",
                    })
                );
                formset.append(
                    $("<input>", {
                        name: prefix + "-" + next_index + "-announcement",
                        value: attachments_to_delete[i].announcement,
                        type: "hidden",
                    })
                );
                formset.append(
                    $("<input>", {
                        name: prefix + "-" + next_index + "-DELETE",
                        value: "on",
                        type: "hidden",
                    })
                );
                next_index++;
            }
        }
        return true;
    };

    form.on("submit", form_submit_handler.bind(this));

    draft_button.on("click", (e) => {
        e.preventDefault();
        announcement_status.val("0");
        form.trigger("submit");
    });

    publish_button.on("click", (e) => {
        e.preventDefault();
        announcement_status.val("1");
        form.trigger("submit");
    });

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

    const formset = $("#formset");
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
    const get_attachment_rows = (include_empty) => {
        if (include_empty)
            return formset.find("tr[id^=Announcement_attachments-]");
        return formset.find("tr[id^=Announcement_attachments-]:not(.d-none)");
    };

    const template = formset.find(".d-none.empty-form");

    get_attachment_rows(false)
        .find("select")
        .map((i, el) => {
            Tags.init("#" + el.id, {
                placeholder: "請選擇一個檔案",
            });
        });

    const update_element_index = (el, prefix, idx) => {
        const id_regex = new RegExp(prefix + "-(\\d+|__prefix__)");
        const replacement = prefix + "-" + idx;
        if ($(el).prop("for"))
            $(el).prop("for", $(el).prop("for").replace(id_regex, replacement));
        if (el.id) el.id = el.id.replace(id_regex, replacement);
        if (el.name) el.name = el.name.replace(id_regex, replacement);
    };

    const add_inline_click_handler = (e) => {
        e.preventDefault();
        const row = template.clone(true);
        row.attr("id", prefix + "-" + next_index);
        row.children(":first").removeAttr("id");
        row.removeClass("d-none");
        add_inline_delete_button(row);
        row.find("*").each((i, el) => {
            update_element_index(el, prefix, next_index);
        });
        row.insertBefore(template);
        row.find("select");
        Tags.init("#id_" + prefix + "-" + next_index + "-file", {
            placeholder: "請選擇一個檔案",
        });
        $(total_forms).val(parseInt(total_forms.val(), 10) + 1);
        next_index++;
        if (max_forms.val() != "" && max_forms.val() - total_forms.val() <= 0) {
            add_button.addClass("disabled");
        }
    };

    const add_button = $("#add_attachment");
    add_button.on("click", add_inline_click_handler.bind(this));

    const add_inline_delete_button = (row) => {
        const delete_button_location = row.children(":last");
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
            "tr[id^=Announcement_attachments]:not(.d-none)"
        );
        if (row.hasClass("has_original")) {
            attachments_to_delete.push({
                id: row.find("input[type=hidden][name$=id]").val(),
                file: row.find("select").val(),
                announcement: row
                    .find("input[type=hidden][name$=announcement]")
                    .val(),
            });
            console.log(attachments_to_delete);
        }
        row.remove();
        next_index--;
        const forms = get_attachment_rows(false);
        total_forms.val(forms.length);
        if (max_forms.val() != "" && max_forms.val() - forms.length > 0) {
            add_button.removeClass("disabled");
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
        .find("tr[id^=Announcement_attachments]:not(.d-none)")
        .each((i, el) => {
            const row = $(el);
            add_inline_delete_button(row);
        });

    const file_upload_form = $("#file_upload_form");
    const file_upload_modal = file_upload_form.closest(".modal");
    const upload_button = file_upload_modal.find("button.btn-primary");
    upload_button.on("click", (e) => {
        e.preventDefault();
        file_upload_form.trigger("submit");
    });

    const file_input = file_upload_form.find("input[type=file]");
    file_upload_form.on("submit", (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        $.ajax({
            type: "POST",
            url: dataset.uploadFileUrl,
            data: formData,
            processData: false,
            contentType: false,
            enctype: "multipart/form-data",
            success: handle_file_upload_success,
            error: (xhr) => {
                file_input.addClass("is-invalid");

                if (file_input.next().hasClass("invalid-feedback")) {
                    file_input.next().remove();
                }

                $("<div>", {
                    class: "invalid-feedback",
                    text: xhr.responseJSON.error.file[0],
                }).insertAfter(file_input);
            },
        });
    });

    const get_bootstrap5_tag_instance = (el) => {
        return Tags.getInstance(el);
    };

    const update_all_select_inputs = (rows, new_file) => {
        rows.each((i, el) => {
            const row = $(el);
            const select_input = row.find("select").get(0);
            const tag = get_bootstrap5_tag_instance(select_input);
            let data = tag.getData();
            data = [...data, new_file];
            tag.setData(data);
        });
    };

    const select_new_file = (new_file) => {
        const select_inputs = get_attachment_rows().find("select");
        let empty_select_input = select_inputs
            .filter((e, el) => {
                return $(el).val() == "";
            })
            .get(0);

        if (empty_select_input == undefined) {
            // if there is no empty select input, add a new row
            if (
                max_forms.val() != "" &&
                max_forms.val() - total_forms.val() > 0
            ) {
                add_button.trigger("click");
                empty_select_input = get_attachment_rows()
                    .find("select")
                    .last()
                    .get(0);
            }
            // no empty select input and max_forms is reached
            else return;
        }
        const tag = get_bootstrap5_tag_instance(empty_select_input);
        tag.setItem(new_file.value);
    };

    const update_empty_select_input = (new_file) => {
        let opt = $("<option>", {
            value: new_file.value,
        }).text(new_file.label);
        $("#" + prefix + "-empty")
            .find("select")
            .append(opt);
    };

    const handle_file_upload_success = (res) => {
        file_upload_form.trigger("reset");
        file_upload_modal.modal("hide");
        file_input.removeClass("is-invalid");
        update_empty_select_input(res.object);
        update_all_select_inputs(get_attachment_rows(false), res.object);
        select_new_file(res.object);
    };
});
