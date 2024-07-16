import "../scss/styles.scss";
import "../scss/vendors/quill/quill.scss";
import "../scss/vendors/litepicker/litepicker.scss";
import Quill from "./quill";

import "./nifty";

import Litepicker from "litepicker";
import Tags from "bootstrap5-tags";

window.Tags = Tags;
window.$ = require("jquery");
window.jQuery = require("jquery");
window.Litepicker = Litepicker;
window.Quill = Quill;
