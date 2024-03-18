<template>
    <svg :style="size"
         :viewBox="`0 0 ${originalWidth} ${originalHeight}`"
         id="map"
         xml:space="preserve"
         xmlns="http://www.w3.org/2000/svg">

        <!-- нет -->
        <path class="part" id="no"
              d="M 39.6875,25.135417 A 11.90625,11.90625 0 1 0 27.78125,13.229167 11.90625,11.90625 0 0 0 39.6875,25.135417 Z"
              @mousedown="mouse('down', 'Нет')"
              :fill="color('Нет','#dc0909')"/>
        <path
            d="m 34.079315,14.789149 h 2.046387 a 0.42245483,0.42245483 0 0 0 0.420517,-0.422454 V 8.7565719 A 0.4243927,0.4243927 0 0 0 36.125702,8.334117 H 34.079315 A 0.4243927,0.4243927 0 0 0 33.65686,8.7565719 v 5.6101231 a 0.4243927,0.4243927 0 0 0 0.422455,0.422454 z m 5.36789,4.207108 c 0.220916,1.127838 2.065765,0.08914 2.18785,-1.726639 a 7.8309173,7.8309173 0 0 0 -0.156967,-1.924301 h 2.637436 c 1.094895,-0.04457 2.052201,-0.829407 1.375885,-2.118088 0.155029,-0.561981 0.178284,-1.220856 -0.240295,-1.482467 0.05232,-0.885605 -0.193787,-1.435959 -0.653061,-1.8700413 A 2.2130432,2.2130432 0 0 0 44.253113,8.7352553 C 43.898483,8.2352859 43.611679,8.3476821 43.053574,8.3476821 h -4.457093 c -0.705383,0 -1.089081,0.1937866 -1.550293,0.7751465 V 14.08958 c 1.339066,0.354629 2.044449,2.17041 2.401017,3.362198 v 1.550292 z"
            id="no-hand" @mousedown="mouse('down', 'Нет')"
            style="fill:#ffffff"/>
        <text
            xml:space="preserve"
            style="font-size:3.52094px;text-align:center;text-anchor:middle;fill:#000000;fill-opacity:1;stroke-width:0.264999"
            x="39.775723"
            y="29.087042"
            id="text4756-0">
            <tspan
                id="tspan4754-9"
                x="39.775723"
                y="29.087042"
                style="font-size:3.52094px;fill:#000000;stroke-width:0.265">
                Нет
            </tspan>
        </text>


        <!-- да -->
        <path class="part"
              :fill="color('Да', '#50b432')"
              @mousedown="mouse('down', 'Да')"
              d="M 13.229166,1.3229167 A 11.90625,11.90625 0 1 0 25.135417,13.229167 11.90625,11.90625 0 0 0 13.229166,1.3229167 Z"
              id="yes"
        />
        <path
            style="fill:#ffffff" @mousedown="mouse('down', 'Да')"
            d="m 18.945082,11.633194 h -2.050361 a 0.42327534,0.42327534 0 0 0 -0.421333,0.423276 v 5.621019 a 0.42521697,0.42521697 0 0 0 0.421333,0.423275 h 2.050361 a 0.42521697,0.42521697 0 0 0 0.423276,-0.423275 V 12.05647 A 0.42521697,0.42521697 0 0 0 18.945082,11.633194 Z M 13.566767,7.4179157 c -0.221345,-1.1300286 -2.069777,-0.089315 -2.1921,1.7299924 a 7.8461268,7.8461268 0 0 0 0.157272,1.9280389 H 8.8893807 c -1.0970209,0.04466 -2.0561861,0.831017 -1.3785573,2.122201 -0.1553304,0.563073 -0.1786299,1.223227 0.2407621,1.485347 -0.052424,0.887325 0.194163,1.438748 0.6543294,1.873673 a 2.2173415,2.2173415 0 0 0 0.3456101,1.141679 c 0.3553183,0.50094 0.6426795,0.388326 1.201869,0.388326 h 4.465749 c 0.706753,0 1.091196,-0.194163 1.553304,-0.776652 v -4.976398 c -1.341666,-0.355318 -2.04842,-2.174626 -2.40568,-3.3687282 v -1.553304 z"
            id="yes-hand"/>

        <text
            xml:space="preserve"
            style="font-size:3.52778px;text-align:center;text-anchor:middle;fill:#000000;fill-opacity:1;stroke-width:0.264999"
            x="13.469838"
            y="28.913151"
            id="text4756">
            <tspan
                id="tspan4754"
                x="13.469838"
                y="28.913151"
                style="font-size:3.52778px;fill:#000000;stroke-width:0.265">
                Да
            </tspan>
        </text>
       </svg>
</template>

<script>
export default {
    name: "YesNoMap",
    props: ['parts', 'width', 'uid'],
    data() {
        return {
            originalWidth: 52,
            originalHeight: 30
        }
    },
    computed: {
        size() {
            let w = this.mobile ? window.innerWidth * 0.7 : 400
            return `width: ${w}px; height: ${this.originalHeight * this.proportion}px;`
        },
        proportion() {
            let w = this.mobile ? window.innerWidth * 0.7 : 400
            return w / this.originalWidth
        }
    },
    methods: {
        mouse: function (action, zone) {
            Event.fire(`mouse-${action}`, {zone: zone, uid: this.uid})
        },
        color: function (zone, color) {
            return this.parts.filter(p => p == zone).length ? color : (color + '99')
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
