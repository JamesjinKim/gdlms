export default {
  template: `
        <span>
              <span :style="{color:cellColor}">{{ cellValue }}</span>             
          </span>
    `,
  setup(props) {
    const cellValue = props.params.valueFormatted
      ? props.params.valueFormatted
      : props.params.value;
    const cellColor = props.params.color;
    console.log(cellColor);

    return {
      cellValue,
      cellColor,
    };
  },
};
