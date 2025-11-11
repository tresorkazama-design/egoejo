import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { api } from "../config/api.js";

gsap.registerPlugin(ScrollTrigger);

const PROFILS = [
  { value: "je-decouvre", label: "Je découvre" },
  { value: "je-protege", label: "Je protège" },
  { value: "je-soutiens", label: "Je soutiens" },
];

