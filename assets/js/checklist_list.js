const data = document.currentScript.dataset;

$(() => {
    data.checklistChangeStatusUrl;

    // filter id start with id-checklist-
    $("input[type=checkbox][id^=id-checklist-]").on("change", (e) => {
        const checklist = $(e.target);
        const checklistId = checklist.attr("id").replace("id-checklist-", "");
        const status = checklist.is(":checked") ? "done" : "todo";

        $.ajax({
            url: data.checklistChangeStatusUrl,
            method: "POST",
            data: JSON.stringify({
                checklist: checklistId,
                status: status,
            }),
            dataType: "json",
            contentType: "application/json",
            success: (response) => {
                console.log(response);
            },
        });
    });
});
