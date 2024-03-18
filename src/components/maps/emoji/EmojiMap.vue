<template>
    <svg :style="size"
         :viewBox="`0 0 ${originalWidth} ${originalHeight}`"
         id="map"
         xml:space="preserve"
         xmlns="http://www.w3.org/2000/svg">

        <!--        Отлично -->
        <path class="part"
              d="m 48.51252,32.158499 c 6.350567,-1.701494 12.877485,2.067762 14.57898,8.416392 1.701495,6.350567 -2.067762,12.877485 -8.416391,14.57898 C 48.324541,56.855366 41.797623,53.086109 40.096128,46.73748 38.394634,40.386912 42.161952,33.859994 48.51252,32.158499 Z"
              id="5" style="stroke: #000000; stroke-linejoin: miter"
              @mousedown="mouse('down', 'Отлично')"
              :fill="color('Отлично','#fbd433')" :stroke-width="stroke('Отлично')"/>
        <path
            d="m 47.805178,37.148646 c 0.833307,0 1.507703,0.951519 1.507703,2.1259 0,1.17438 -0.674396,2.125899 -1.507703,2.125899 -0.833306,0 -1.507702,-0.951519 -1.507702,-2.125899 0,-1.174381 0.674396,-2.1259 1.507702,-2.1259 z m -2.585186,7.608278 c 3.232452,-0.100771 9.885335,0.0562 12.747645,-0.0078 0,7.707112 -12.747645,8.443522 -12.747645,0.0078 z M 55.38245,37.148646 c 0.833306,0 1.507703,0.951519 1.507703,2.1259 0,1.17438 -0.674397,2.125899 -1.507703,2.125899 -0.833306,0 -1.507703,-0.951519 -1.507703,-2.125899 0,-1.174381 0.674397,-2.1259 1.507703,-2.1259 z"
            id="path4932" @mousedown="mouse('down', 'Отлично')"
            style="stroke-width:0.193792"/>
        <path
            d="m 45.219992,44.756924 c 3.232452,-0.294564 9.885335,-0.12984 12.747645,-0.0078 0.03682,2.742158 -12.708887,2.707276 -12.747645,0.0078 z"
            id="path4934" @mousedown="mouse('down', 'Отлично')"
            style="stroke-width:0.193792"/>
        <path
            class="st3"
            d="m 47.167602,49.37499 c 2.153031,1.862343 6.170341,1.935984 8.584991,0 -1.313911,-1.494137 -2.747972,-1.540647 -4.339005,-0.364329 -1.639482,-1.311972 -2.738283,-1.348793 -4.245986,0.364329 z"
            id="path4936" @mousedown="mouse('down', 'Отлично')"
            style="stroke-width:0.193792"/>

        <!--        Хорошо -->
        <path class="part"
              d="M 22.054061,32.155639 A 11.90625,11.90625 0 1 1 13.635168,46.738953 11.90625,11.90625 0 0 1 22.054061,32.155639 Z"
              id="4" style="stroke: #000000; stroke-linejoin: miter"
              @mousedown="mouse('down', 'Хорошо')"
              :fill="color('Хорошо','#ffc800')" :stroke-width="stroke('Хорошо')"/>
        <path
            d="m 22.100585,38.002146 c 0.833554,0 1.51009,0.969249 1.51009,2.184687 0,1.215438 -0.676536,2.184686 -1.51009,2.184686 -0.833554,0 -1.508151,-0.977002 -1.508151,-2.184686 0,-1.207684 0.674597,-2.184687 1.508151,-2.184687 z"
            id="path5105" @mousedown="mouse('down', 'Хорошо')"/>
        <path
            d="m 28.171958,38.002146 c 0.833554,0 1.508151,0.969249 1.508151,2.184687 0,1.215438 -0.674597,2.184686 -1.508151,2.184686 -0.833553,0 -1.510089,-0.969248 -1.510089,-2.184686 0,-1.215438 0.676536,-2.184687 1.510089,-2.184687 z"
            id="path5107" @mousedown="mouse('down', 'Хорошо')"
            style="stroke-width:0.19385"/>
        <path
            d="m 18.809017,45.475053 a 7.6861414,7.6861414 0 0 0 1.711693,1.630276 8.28126,8.28126 0 0 0 4.846243,1.459689 7.8392827,7.8392827 0 0 0 4.675655,-1.57406 6.9301275,6.9301275 0 0 0 1.451935,-1.525597 0.04264694,0.04264694 0 0 1 0.06009,0 l 0.474932,0.459424 a 0.04070844,0.04070844 0 0 1 0,0.05622 8.8918867,8.8918867 0 0 1 -2.73522,2.936823 7.302319,7.302319 0 0 1 -3.888625,1.244515 7.5601391,7.5601391 0 0 1 -4.008812,-1.075866 9.7932879,9.7932879 0 0 1 -3.150058,-3.078333 0.04458544,0.04458544 0 0 1 0,-0.05428 l 0.488501,-0.484624 a 0.04264694,0.04264694 0 0 1 0.06203,0 v 0 z"
            id="path5109" @mousedown="mouse('down', 'Хорошо')"
            style="stroke-width:0.19385"/>

        <!-- Удовлетворительно -->
        <path class="part"
              @mousedown="mouse('down', 'Удовлетворительно')"
              :fill="color('Удовлетворительно','#f18100')" :stroke-width="stroke('Удовлетворительно')"
              id="3" style="stroke: #000000; stroke-linejoin: miter"
              d="M 77.64639,10.147648 A 11.906293,11.90625 82.500023 0 1 69.227395,24.729808 11.906293,11.90625 82.500023 0 1 54.645278,16.31077 11.906293,11.90625 82.500023 0 1 63.064273,1.72861 11.906293,11.90625 82.500023 0 1 77.64639,10.147648 Z"/>
        <path
            fill="#40270e"
            @mousedown="mouse('down', 'Удовлетворительно')"
            d="m 60.807197,18.3599 c -0.515261,0 -0.932967,-0.417707 -0.932967,-0.932921 0,-0.51526 0.417706,-0.932967 0.932967,-0.932967 h 10.677366 c 0.515261,0 0.932967,0.417707 0.932967,0.932967 0,0.515214 -0.417706,0.932921 -0.932967,0.932921 z m 1.242467,-8.7823111 c 0.876259,0 1.586579,0.8992861 1.586579,2.0086121 0,1.109373 -0.71032,2.008612 -1.586579,2.008612 -0.876166,0 -1.586486,-0.899239 -1.586486,-2.008612 0,-1.109326 0.71032,-2.0086121 1.586486,-2.0086121 z m 8.192293,0 c 0.876258,0 1.586532,0.8992861 1.586532,2.0086121 0,1.109373 -0.710274,2.008612 -1.586532,2.008612 -0.876259,0 -1.586579,-0.899239 -1.586579,-2.008612 0,-1.109326 0.71032,-2.0086121 1.586579,-2.0086121 z"
            id="path4958"/>

        <!-- Плохо -->
        <path class="part"
              @mousedown="mouse('down', 'Плохо')"
              :fill="color('Плохо','#f16400')" :stroke-width="stroke('Плохо')"
              id="2" style="stroke: #000000; stroke-linejoin: miter"
              d="M 51.188051,10.147637 A 11.906292,11.906249 82.499996 0 1 42.76907,24.729803 11.906292,11.906249 82.499996 0 1 28.186947,16.310779 11.906292,11.906249 82.499996 0 1 36.605928,1.7286127 11.906292,11.906249 82.499996 0 1 51.188051,10.147637 Z"/>
        <path
            fill="#40270e" @mousedown="mouse('down', 'Плохо')"
            d="m 35.111875,18.957871 c -0.404729,0.177336 -0.800992,-0.22716 -0.397705,-0.643892 3.260907,-2.899721 6.685799,-2.899721 9.946659,0 0.403333,0.416732 0.0071,0.821228 -0.397658,0.643892 -2.973549,-1.776575 -6.177747,-1.776575 -9.151296,0 z"
            id="path11164"/>
        <path
            fill="#40270e" @mousedown="mouse('down', 'Плохо')"
            d="m 43.78359,8.1807018 c 0.876355,0 1.586631,0.8993359 1.586631,2.0086652 0,1.10933 -0.710276,2.00862 -1.586631,2.00862 -0.876169,0 -1.586491,-0.89929 -1.586491,-2.00862 0,-1.1093293 0.710322,-2.0086652 1.586491,-2.0086652 z m -8.192181,0 c 0.876215,0 1.586538,0.8993359 1.586538,2.0086652 0,1.10933 -0.710323,2.00862 -1.586538,2.00862 -0.876308,0 -1.586584,-0.89929 -1.586584,-2.00862 0,-1.1093293 0.710276,-2.0086652 1.586584,-2.0086652 z"
            id="path11289"/>


        <!-- Очень плохо -->
        <path class="part" style="stroke: #000000; stroke-linejoin: miter"
              @mousedown="mouse('down', 'Очень плохо')"
              :fill="color('Очень плохо','#f14000')"  :stroke-width="stroke('Очень плохо')"
              d="M 10.147936,1.7314163 C 16.498504,0.02992146 23.025422,3.7991782 24.726917,10.147808 26.428412,16.498376 22.659155,23.025294 16.310525,24.726789 9.9599576,26.428284 3.433039,22.659027 1.7315442,16.310397 0.03004936,9.9598297 3.7973682,3.4329111 10.147936,1.7314163 Z"
              id="1"/>
        <path
            d="m 10.194446,7.5761866 c 0.833306,0 1.507703,0.9786502 1.507703,2.1840372 0,1.2053872 -0.674397,2.1840372 -1.507703,2.1840372 -0.8333061,0 -1.5077026,-0.97865 -1.5077026,-2.1840372 0,-1.205387 0.6743965,-2.1840372 1.5077026,-2.1840372 z M 6.7720772,19.674629 c 3.2343908,-4.191724 9.8853358,-4.100642 12.7476458,0.0078 l 0.467039,-0.463163 C 16.78144,13.779472 9.9948402,13.58568 6.285659,19.190148 Z M 16.264015,7.5761866 c 0.833306,0 1.507703,0.9786502 1.507703,2.1840372 0,1.2053872 -0.674397,2.1840372 -1.507703,2.1840372 -0.833306,0 -1.507702,-0.97865 -1.507702,-2.1840372 -0.0019,-1.205387 0.674396,-2.1840372 1.507702,-2.1840372 z"
            @mousedown="mouse('down', 'Очень плохо')"
            id="path9666"/>


        <text
            xml:space="preserve"
            style="font-size:3.5px;text-align:center;text-anchor:middle;clip-rule:evenodd;display:inline;fill:#dc0909;fill-opacity:1;fill-rule:evenodd;stroke-width:0.264999;image-rendering:optimizeQuality;shape-rendering:geometricPrecision;text-rendering:geometricPrecision"
            x="39.68285"
            y="27.997259"
            id="text4756-3">
            <tspan
                id="tspan4754"
                x="39.68285"
                y="27.997259"
                style="font-size:3.5px;fill:#000000;stroke-width:0.264999">
                Плохо
            </tspan>
        </text>

        <text
            xml:space="preserve"
            style="font-size:3.5px;text-align:center;text-anchor:middle;clip-rule:evenodd;display:inline;fill:#dc0909;fill-opacity:1;fill-rule:evenodd;stroke-width:0.264999;image-rendering:optimizeQuality;shape-rendering:geometricPrecision;text-rendering:geometricPrecision"
            x="13.224516"
            y="28.029299"
            id="text21026">
            <tspan
                id="tspan21024"
                x="13.224516"
                y="28.029299"
                style="font-size:3.5px;fill:#000000;stroke-width:0.264999">
                Очень плохо
            </tspan>
        </text>

        <text
            xml:space="preserve"
            style="font-size:3.5px;text-align:center;text-anchor:middle;clip-rule:evenodd;display:inline;fill:#dc0909;fill-opacity:1;fill-rule:evenodd;stroke-width:0.264999;image-rendering:optimizeQuality;shape-rendering:geometricPrecision;text-rendering:geometricPrecision"
            x="66.19751"
            y="27.997259"
            id="text21030">
            <tspan
                id="tspan21028"
                x="66.19751"
                y="27.997259"
                style="font-size:3.5px;fill:#000000;stroke-width:0.264999">
                Удовлетворительно
            </tspan>
        </text>


        <text
            xml:space="preserve"
            style="font-size:3.5px;text-align:center;text-anchor:middle;clip-rule:evenodd;display:inline;fill:#dc0909;fill-opacity:1;fill-rule:evenodd;stroke-width:0.264999;image-rendering:optimizeQuality;shape-rendering:geometricPrecision;text-rendering:geometricPrecision"
            x="25.155054"
            y="58.424343"
            id="text21034">
            <tspan
                id="tspan21032"
                x="25.155054"
                y="58.424343"
                style="font-size:3.5px;fill:#000000;stroke-width:0.264999">
                Хорошо
            </tspan>
        </text>

        <text
            xml:space="preserve"
            style="font-size:3.5px;text-align:center;text-anchor:middle;fill:#141518;fill-opacity:1;stroke-width:0.264999"
            x="51.5891"
            y="58.456383"
            id="text21038">
            <tspan
                id="tspan21036"
                style="stroke-width:0.265"
                x="51.5891"
                y="58.456383">
                Отлично
            </tspan>
        </text>
    </svg>
</template>

<script>
export default {
    name: "EmojiMap",
    props: ['parts', 'width', 'uid'],
    data() {
        return {
            originalWidth: 80,
            originalHeight: 62
        }
    },
    computed: {
        size() {
            let w = this.mobile ? window.innerWidth * 0.8 : 400
            return `width: ${w}px; height: ${this.originalHeight * this.proportion}px;`
        },
        proportion() {
            let w = this.mobile ? window.innerWidth * 0.8 : 400
            return w / this.originalWidth
        }
    },
    methods: {
        mouse: function (action, zone) {
            Event.fire(`mouse-${action}`, {zone: zone, uid: this.uid})
        },
        color: function (zone, color) {
            return this.parts.filter(p => p == zone).length ? color : (color + '99')
        },
        stroke: function (zone) {
            return this.parts.filter(p => p == zone).length ? '1px' : '0'
        }
    }
}
</script>

<style scoped>
@media (hover: hover) and (pointer: fine) {
    path.part:hover {
        stroke-width: 0.5px !important;
    }
}
</style>
