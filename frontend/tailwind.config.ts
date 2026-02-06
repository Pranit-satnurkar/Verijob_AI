import type { Config } from "tailwindcss";
import colors from "tailwindcss/colors";

const config: Config = {
    darkMode: "class",
    content: [
        "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
        "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                // Redifine primary as Zinc 900 (Dark) / Zinc 100 (Light) for high contrast
                primary: colors.zinc[900],
                zinc: colors.zinc,
            },
            fontFamily: {
                display: ["Inter", "sans-serif"],
                mono: ["monospace"], // Raw technical feel
            },
        },
    },
    plugins: [],
};
export default config;
