export default {
  template: `
        <span>
              <span>{{ cellValue }}</span>
              <button @click.stop="buttonClicked()">Call Method</button>
          </span>
    `,
  setup(props) {
    const cellValue = props.params.valueFormatted
      ? props.params.valueFormatted
      : props.params.value;
    const buttonClicked = () => {
      console.log(props.params.context.componentParent);
      props.params.context.componentParent.callMethod(cellValue);
    };

    // props.params contains the cell and row information and is made available to this component at creation time
    // see ICellRendererParams for more details
    return {
      cellValue,
      buttonClicked,
    };
  },
};
