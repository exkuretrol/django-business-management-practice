import "../scss/styles.scss";
import "../scss/vendors/quill/quill.scss";
import "../scss/vendors/litepicker/litepicker.scss";

import "./nifty";
import Quill from "./quill";

import Litepicker from "litepicker";
import Tags from "bootstrap5-tags";

window.Tags = Tags;
window.$ = require("jquery");
window.jQuery = require("jquery");
window.Quill = Quill;
window.Litepicker = Litepicker;
