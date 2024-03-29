<template>
    <svg
        :style="size"
        :viewBox="`50 29 ${originalWidth} ${originalHeight}`"
        ::id="'map_' + uid"
        xml:space="preserve"
        xmlns="http://www.w3.org/2000/svg">
        <path
            class="part"
            :fill="color('1')"
            @mousedown="mouse('down', '1')"
            d="m 94.220759,40.069481 11.823781,0.04106 V 29.354179 c 0,0 -11.084794,0.205274 -11.823781,10.715302 z"
            :id="'1_' + uid"/>
        <path
            class="part"
            :fill="color('2')"
            @mousedown="mouse('down', '2')"
            d="m 118.40204,40.028425 -11.82378,0.04106 V 29.313123 c 0,0 11.0848,0.205274 11.82378,10.715302 z"
            :id="'2_' + uid"/>
        <path
            class="part"
            :fill="color('3')"
            @mousedown="mouse('down', '3')"
            d="m 94.097596,40.651976 h 11.946944 v 13.096481 h -9.524711 c 0,0 -3.038056,-6.815095 -2.422233,-13.096481 z"
            :id="'3_' + uid"/>
        <path
            class="part"
            :fill="color('4')"
            @mousedown="mouse('down', '4')"
            d="m 118.54558,40.664777 h -11.94694 v 13.096481 h 9.52471 c 0,0 3.03806,-6.815095 2.42223,-13.096481 z"
            :id="'4_' + uid"/>
        <path
            class="part"
            :fill="color('5')"
            @mousedown="mouse('down', '5')"
            d="m 96.652769,54.136867 h 9.401691 v 8.324038 c 0,0 -6.342428,-0.586312 -9.401691,-8.324038 z"
            :id="'5_' + uid"/>
        <path
            class="part"
            :fill="color('6')"
            @mousedown="mouse('down', '6')"
            d="m 115.98087,54.140298 h -9.4017 v 8.324038 c 0,0 6.34244,-0.586312 9.4017,-8.324038 z"
            :id="'6_' + uid"/>
        <path
            class="part"
            :fill="color('7')"
            @mousedown="mouse('down', '7')"
            d="m 97.019094,64.066061 h 9.041256 V 63.51504 c 0,0 -4.12857,-0.306831 -7.555439,-4.823671 -0.452964,5.606735 -1.485817,5.374692 -1.485817,5.374692 z"
            :id="'7_' + uid"/>
        <path
            class="part"
            :fill="color('8')"
            @mousedown="mouse('down', '8')"
            d="m 115.62872,64.065631 h -9.04125 V 63.51461 c 0,0 4.12857,-0.306831 7.55543,-4.823671 0.45297,5.606735 1.48582,5.374692 1.48582,5.374692 z"
            :id="'8_' + uid"/>
        <path
            class="part"
            :fill="color('9')"
            @mousedown="mouse('down', '9')"
            d="m 95.922597,64.657116 -6.364569,2.869503 V 78.883366 H 106.03043 V 64.661851 Z"
            :id="'9_' + uid"/>
        <path
            class="part"
            :fill="color('10')"
            @mousedown="mouse('down', '10')"
            d="m 116.69784,64.615666 6.36457,2.869503 v 11.356747 h -16.4724 V 64.620401 Z"
            :id="'10_' + uid"/>
        <path
            class="part"
            :fill="color('17')"
            @mousedown="mouse('down', '17')"
            d="M 72.432893,78.864128 H 89.148178 V 67.661334 c 0,0 -12.447553,4.297368 -13.959041,6.549782 -1.511488,2.252413 -1.689309,2.459873 -2.756244,4.653012 z"
            :id="'17_' + uid"/>
        <path
            class="part"
            :fill="color('24')"
            @mousedown="mouse('down', '24')"
            d="M 140.22537,78.813519 H 123.51008 V 67.610725 c 0,0 12.44756,4.297368 13.95905,6.549782 1.51148,2.252413 1.6893,2.459873 2.75624,4.653012 z"
            :id="'24_' + uid"/>
        <path
            class="part"
            :fill="color('16')"
            @mousedown="mouse('down', '16')"
            d="m 72.226275,79.430778 h 10.512232 v 16.040214 h -9.832562 c 0,0 -3.035859,-11.916881 -0.67967,-16.040214 z"
            :id="'16_' + uid"/>
        <path
            class="part"
            :fill="color('23')"
            @mousedown="mouse('down', '23')"
            d="m 140.4979,79.470213 h -10.5123 v 16.040214 h 9.83262 c 0,0 3.03588,-11.916881 0.67968,-16.040214 z"
            :id="'23_' + uid"/>
        <path
            class="part"
            :fill="color('25')"
            @mousedown="mouse('down', '25')"
            d="M 83.377763,79.45193 H 94.79347 V 91.872795 H 83.305965 V 79.447152"
            :id="'25_' + uid"/>
        <path
            class="part"
            :fill="color('27')"
            @mousedown="mouse('down', '27')"
            d="m 117.97545,79.50572 h 11.41571 v 12.420865 h -11.4875 V 79.500942"
            :id="'27_' + uid"/>
        <path
            class="part"
            :fill="color('26')"
            @mousedown="mouse('down', '26')"
            d="M 95.217251,79.468392 V 91.958865 H 117.39237 V 79.513646 Z"
            :id="'26_' + uid"/>
        <path
            class="part"
            :fill="color('15')"
            @mousedown="mouse('down', '15')"
            d="m 71.85717,112.33545 -0.512168,0.6146 h 11.114045 l 0.307301,-2.4584 V 95.997282 h -9.833626 c 0,0 -1.536504,6.760628 -1.075552,16.338168 z"
            :id="'15_' + uid"/>
        <path
            class="part"
            :fill="color('22')"
            @mousedown="mouse('down', '22')"
            d="m 140.89175,112.3861 0.51217,0.6146 h -11.11404 l -0.3073,-2.4584 V 96.047924 h 9.83362 c 0,0 1.5365,6.760636 1.07555,16.338176 z"
            :id="'22_' + uid"/>
        <path
            class="part"
            :fill="color('28')"
            @mousedown="mouse('down', '28')"
            d="M 83.194016,110.74125 V 92.514509 h 11.529793 v 27.754351 h -8.561044 c 0,0 -0.552325,-4.14244 -2.968749,-9.52761 z"
            :id="'28_' + uid"/>
        <path
            class="part"
            :fill="color('30')"
            @mousedown="mouse('down', '30')"
            d="M 129.5334,110.70194 V 92.475197 h -11.52982 v 27.754353 h 8.56107 c 0,0 0.55233,-4.14244 2.96875,-9.52761 z"
            :id="'30_' + uid"/>
        <path
            class="part"
            :fill="color('29')"
            @mousedown="mouse('down', '29')"
            d="M 95.217251,92.482513 V 120.22322 H 117.39237 V 92.58302 Z"
            :id="'29_' + uid"/>
        <path
            class="part"
            :fill="color('14')"
            @mousedown="mouse('down', '14')"
            d="M 71.062833,113.46422 H 82.37212 c 0,0 -0.849596,9.43138 -0.785099,11.40354 0.0333,1.01826 -0.936614,4.12563 -0.936614,4.12563 H 67.079261 c 0,0 0.349366,-7.87293 0.336024,-8.66274 -0.01065,-0.63058 1.525429,-4.21988 3.647548,-6.86643 z"
            :id="'14_' + uid"/>
        <path
            class="part"
            :fill="color('21')"
            @mousedown="mouse('down', '21')"
            d="M 141.66085,113.46422 H 130.3515 c 0,0 0.8496,9.43138 0.78511,11.40354 -0.0333,1.01826 0.93662,4.12563 0.93662,4.12563 h 13.57122 c 0,0 -0.34937,-7.87293 -0.33603,-8.66274 0.0106,-0.63058 -1.52543,-4.21988 -3.64757,-6.86643 z"
            :id="'21_' + uid"/>
        <path
            class="part"
            :fill="color('13')"
            @mousedown="mouse('down', '13')"
            d="M 61.976843,149.09524 H 70.8446 c 0,0 4.09281,-9.50117 6.041768,-12.71695 1.948958,-3.21578 3.361952,-6.57773 3.361952,-6.77263 0,-0.19489 -13.25291,0 -13.25291,0 0,0 -0.34107,5.45708 -0.779585,6.23667 -0.438515,0.77958 -2.241301,5.89559 -4.238982,13.25291 z"
            :id="'13_' + uid"/>
        <path
            class="part"
            :fill="color('20')"
            @mousedown="mouse('down', '20')"
            d="m 150.77429,149.09524 h -8.86781 c 0,0 -4.09283,-9.50117 -6.0418,-12.71695 -1.949,-3.21578 -3.362,-6.57773 -3.362,-6.77263 0,-0.19489 13.25301,0 13.25301,0 0,0 0.34107,5.45708 0.77959,6.23667 0.43852,0.77958 2.24131,5.89559 4.23901,13.25291 z"
            :id="'20_' + uid"/>
        <path
            class="part"
            :fill="color('31')"
            @mousedown="mouse('down', '31')"
            d="M 82.307313,143.02069 H 94.73612 v -22.21984 h -8.539218 c 0,0 0.703092,1.13388 -3.889589,22.21984 z"
            :id="'31_' + uid"/>
        <path
            class="part"
            :fill="color('33')"
            @mousedown="mouse('down', '33')"
            d="m 130.42594,142.98899 h -12.42888 v -22.21984 h 8.53927 c 0,0 -0.7031,1.13388 3.88961,22.21984 z"
            :id="'33_' + uid"/>
        <path
            class="part"
            :fill="color('32')"
            @mousedown="mouse('down', '32')"
            d="m 95.217251,120.74448 v 22.27048 h 22.175119 v -22.18979 z"
            :id="'32_' + uid"/>
        <path
            class="part"
            :fill="color('12')"
            @mousedown="mouse('down', '12')"
            d="m 69.304809,152.72979 1.227842,-3.0696 h -8.458462 v 24.21575 c 0,0 8.117392,-8.32203 7.23062,-21.14615 z"
            :id="'12_' + uid"/>
        <path
            class="part"
            :fill="color('19')"
            @mousedown="mouse('down', '19')"
            d="m 143.38074,152.66158 -1.22785,-3.0696 h 8.45851 v 24.21575 c 0,0 -8.11744,-8.32203 -7.23066,-21.14615 z"
            :id="'19_' + uid"/>
        <path
            class="part"
            :fill="color('11')"
            @mousedown="mouse('down', '11')"
            d="m 61.543067,149.74681 v 24.66512 c 0,0 -4.607664,4.23891 -5.707301,-0.15964 -0.798224,-3.19289 0.630354,-15.73879 0.319289,-15.40572 -0.551598,0.59062 -4.150765,2.83369 -4.150765,2.83369 l -1.636358,0.19956 c 0,0 7.263836,-12.13301 11.175135,-12.13301 z"
            :id="'11_' + uid"/>
        <path
            class="part"
            :fill="color('18')"
            @mousedown="mouse('down', '18')"
            d="M 151.13302,149.62288 V 174.288 c 0,0 4.60769,4.23891 5.70733,-0.15964 0.79823,-3.19289 -0.63036,-15.73879 -0.31929,-15.40572 0.5516,0.59062 4.15079,2.83369 4.15079,2.83369 l 1.63637,0.19956 c 0,0 -7.26388,-12.13301 -11.1752,-12.13301 z"
            :id="'18_' + uid"/>
        <path
            class="part"
            :fill="color('34')"
            @mousedown="mouse('down', '34')"
            d="m 82.254862,143.55422 h 12.522547 v 19.40995 h -14.33136 c 0,0 0.486989,-15.02706 1.808813,-19.40995 z"
            :id="'34_' + uid"/>
        <path
            class="part"
            :fill="color('36')"
            @mousedown="mouse('down', '36')"
            d="m 130.44658,143.59186 h -12.52262 v 19.40995 h 14.33144 c 0,0 -0.48699,-15.02706 -1.80882,-19.40995 z"
            :id="'36_' + uid"/>
        <path
            class="part"
            :fill="color('35')"
            @mousedown="mouse('down', '35')"
            d="m 104.30637,166.59328 -9.09157,0.0391 v -23.08103 h 22.15417 v 23.0883 l -9.07085,-0.0103 c 0,0 -1.89998,-2.50042 -3.99175,-0.0363 z"
            :id="'35_' + uid"/>
        <path
            class="part"
            :fill="color('46')"
            @mousedown="mouse('down', '46')"
            d="m 80.440391,163.5999 h 14.237571 v 19.82685 H 82.668553 c 0,0 -2.605817,-15.55936 -2.228162,-19.82685 z"
            :id="'46_' + uid"/>
        <path
            class="part"
            :fill="color('57')"
            @mousedown="mouse('down', '57')"
            d="m 132.17826,163.5999 h -14.23765 v 19.82685 h 12.00948 c 0,0 2.60583,-15.55936 2.22817,-19.82685 z"
            :id="'57_' + uid"/>
        <path
            class="part"
            :fill="color('47')"
            @mousedown="mouse('down', '47')"
            d="m 95.227511,167.11469 h 9.069529 l -0.36427,16.44393 -8.742757,-0.12142 z"
            :id="'47_' + uid"/>
        <path
            class="part"
            :fill="color('58')"
            @mousedown="mouse('down', '58')"
            d="m 108.30366,167.15917 h 9.06953 v 16.32251 l -8.78697,0.0607 z"
            :id="'58_' + uid"/>
        <path
            class="part"
            :fill="color('44')"
            @mousedown="mouse('down', '44')"
            d="M 82.798223,184.02251 H 94.65375 v 19.56875 h -6.475307 c 0,0 -0.09523,-1.66644 -0.285676,-2.42824 -0.19045,-0.7618 -4.618418,-14.18854 -5.094544,-17.14051 z"
            :id="'44_' + uid"/>
        <path
            class="part"
            :fill="color('55')"
            @mousedown="mouse('down', '55')"
            d="m 129.817,184.02251 h -11.8556 v 19.56875 h 6.47535 c 0,0 0.0952,-1.66644 0.28568,-2.42824 0.19045,-0.7618 4.61844,-14.18854 5.09457,-17.14051 z"
            :id="'55_' + uid"/>
        <path
            class="part"
            :fill="color('45')"
            @mousedown="mouse('down', '45')"
            d="m 95.179867,183.98573 8.765973,0.0607 c -0.0326,6.68672 -0.005,15.49077 -0.15853,19.59688 h -8.644941 z"
            :id="'45_' + uid"/>
        <path
            class="part"
            :fill="color('56')"
            @mousedown="mouse('down', '56')"
            d="m 117.37576,184.01806 -8.766,0.0607 c 0.0326,6.68672 0.005,15.49077 0.15853,19.59688 h 8.64497 z"
            :id="'56_' + uid"/>
        <path
            class="part"
            :fill="color('42')"
            @mousedown="mouse('down', '42')"
            d="m 88.133538,204.11124 h 6.504906 v 16.06395 h -7.099867 c 0,0 2.26949,-3.96098 0.594961,-16.06395 z"
            :id="'42_' + uid"/>
        <path
            class="part"
            :fill="color('53')"
            @mousedown="mouse('down', '53')"
            d="m 124.44048,204.03753 h -6.50495 v 16.06395 h 7.09991 c 0,0 -2.2695,-3.96098 -0.59496,-16.06395 z"
            :id="'53_' + uid"/>
        <path
            class="part"
            :fill="color('43')"
            @mousedown="mouse('down', '43')"
            d="m 103.79131,204.09234 h -8.672842 v 16.10905 h 6.699652 c 0,0 -0.99437,0.95643 1.97319,-16.10905 z"
            :id="'43_' + uid"/>
        <path
            class="part"
            :fill="color('54')"
            @mousedown="mouse('down', '54')"
            d="m 108.70468,204.09234 h 8.67287 v 16.10905 h -6.69967 c 0,0 0.99438,0.95643 -1.9732,-16.10905 z"
            :id="'54_' + uid"/>
        <path
            class="part"
            :fill="color('40')"
            @mousedown="mouse('down', '40')"
            d="m 87.453879,220.6804 h 7.223895 v 18.21956 h -6.584611 c 0,0 -3.332695,-9.5639 -0.639284,-18.21956 z"
            :id="'40_' + uid"/>
        <path
            class="part"
            :fill="color('51')"
            @mousedown="mouse('down', '51')"
            d="m 125.14288,220.6804 h -7.22393 v 18.21956 h 6.58465 c 0,0 3.33271,-9.5639 0.63928,-18.21956 z"
            :id="'51_' + uid"/>
        <path
            class="part"
            :fill="color('41')"
            @mousedown="mouse('down', '41')"
            d="m 101.8456,220.63255 -6.729002,0.0292 v 18.12941 h 8.097792 c 0,0 0.67498,-3.55473 0.42302,-5.98271 -0.48572,-4.6806 -0.76448,-6.1932 -1.79181,-12.17591 z"
            :id="'41_' + uid"/>
        <path
            class="part"
            :fill="color('52')"
            @mousedown="mouse('down', '52')"
            d="m 110.65593,220.69975 6.72903,0.0292 v 18.12941 h -8.09783 c 0,0 -0.67498,-3.55473 -0.42302,-5.98271 0.48572,-4.6806 0.76449,-6.1932 1.79182,-12.17591 z"
            :id="'52_' + uid"/>
        <path
            class="part"
            :fill="color('38')"
            @mousedown="mouse('down', '38')"
            d="m 88.104123,239.44367 h 6.598799 v 16.86817 H 92.94881 Z"
            :id="'38_' + uid"/>
        <path
            class="part"
            :fill="color('49')"
            @mousedown="mouse('down', '49')"
            d="m 124.53151,239.49244 h -6.59884 v 16.86817 h 1.75412 z"
            :id="'49_' + uid"/>
        <path
            class="part"
            :fill="color('39')"
            @mousedown="mouse('down', '39')"
            d="m 103.0523,239.43833 h -7.932966 v 16.93383 h 7.322736 c 0,0 -0.30511,-8.23808 0.61023,-16.93383 z"
            :id="'39_' + uid"/>
        <path
            class="part"
            :fill="color('50')"
            @mousedown="mouse('down', '50')"
            d="m 109.40689,239.43833 h 7.933 v 16.93383 h -7.32276 c 0,0 0.30511,-8.23808 -0.61024,-16.93383 z"
            :id="'50_' + uid"/>
        <path
            class="part"
            :fill="color('37')"
            @mousedown="mouse('down', '37')"
            d="m 92.99836,256.8963 c 0,0 6.670104,0.0692 9.45619,0.0386 0.47984,3.90326 1.53348,4.28965 2.32664,8.66061 0.61881,3.41019 -0.66037,5.23501 -1.21319,9.05046 -0.1944,1.3417 -9.708764,0.82755 -14.178771,-0.19338 -1.197504,-0.27351 -0.650767,-2.03878 0.6362,-3.81328 0.934295,-1.28822 2.305749,-2.32277 3.45522,-4.04795 1.438163,-2.15847 0.02295,-6.05797 -0.482289,-9.69503 z"
            :id="'37_' + uid"/>
        <path
            class="part"
            :fill="color('48')"
            @mousedown="mouse('down', '48')"
            d="m 119.55766,256.8963 c 0,0 -6.67014,0.0692 -9.45624,0.0386 -0.47984,3.90326 -1.53349,4.28965 -2.32665,8.66061 -0.61882,3.41019 0.66037,5.23501 1.21319,9.05046 0.1944,1.3417 9.70882,0.82755 14.17883,-0.19338 1.19751,-0.27351 0.65077,-2.03878 -0.6362,-3.81328 -0.93429,-1.28822 -2.30575,-2.32277 -3.45522,-4.04795 -1.43817,-2.15847 -0.0229,-6.05797 0.48229,-9.69503 z"
            :id="'48_' + uid"/>

        <text
            xml:space="preserve"
            style="font-size:6.35px;line-height:1;display:inline;fill:#000000;stroke-width:0.264583"
            x="63.266518"
            y="34.068066"
            :id="'text2353-7_' + uid">
            <tspan
                :id="'tspan2351-2_' + uid"
                style="font-size:6.35px;text-align:center;text-anchor:middle;fill:#000000;stroke-width:0.264583"
                x="63.266518"
                y="34.068066">Правая</tspan>
            <tspan
                style="font-size:6.35px;text-align:center;text-anchor:middle;fill:#000000;stroke-width:0.264583"
                x="63.266518"
                y="40.418064"
                :id="'tspan452_' + uid">сторона</tspan></text>
        <text
            xml:space="preserve"
            style="font-size:6.35px;line-height:1;display:inline;fill:#000000;stroke-width:0.264583"
            x="149.75137"
            y="34.14576"
            :id="'text2353-7-3_' + uid">
            <tspan
                :id="'tspan2351-2-6_' + uid"
                style="font-size:6.35px;text-align:center;text-anchor:middle;fill:#000000;stroke-width:0.264583"
                x="149.75137"
                y="34.14576">Левая</tspan>
            <tspan
                style="font-size:6.35px;text-align:center;text-anchor:middle;fill:#000000;stroke-width:0.264583"
                x="149.75137"
                y="40.495758"
                :id="'tspan452-5_' + uid">сторона</tspan>
        </text>
    </svg>
</template>

<script>
export default {
    name: "HumanMap",
    props: ['parts', 'width', 'uid'],
    data() {
        return {
            originalWidth: 112,
            originalHeight: 246,
            zone_groups: []
        }
    },
    computed: {
        size() {
            let w = this.mobile ? window.innerWidth * 0.7 : 250
            return `width: ${w}px; height: ${this.originalHeight * this.proportion}px;`
        },
        proportion() {
            let w = this.mobile ? window.innerWidth * 0.7 : 250
            return w / this.originalWidth
        }
    },
    methods: {
        mouse: function (action, zone) {
            let group = this.zone_groups.findIndex((gr) => gr.zones.includes(zone))
            Event.fire(`mouse-${action}`, {zone: zone, uid: this.uid, group_index: group})
        },
        color: function (zone) {
            let group = this.zone_groups.filter((gr) => gr.zones.includes(zone))
            let color = group[0] ? ('#' + group[0].color) : '#24a8b4'

            return this.parts.filter(p => p == zone).length ? color : '#d3d3d3'
        }
    },
    created() {
        Event.listen('map-zone-groups-changed', (data) => {
            if (data.uid == this.uid) {
                this.zone_groups = data.groups
                this.$forceUpdate()
            }
        })
    }
}
</script>

<style scoped>

</style>
