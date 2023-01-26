import React, { useState } from "react";


interface InputProps {
    addInput: (input: string) => any;
    loading: boolean;
}

function Input({addInput}: InputProps) {
  const [inputState, setInputState] = useState<string>('');

  return (
    <input
      type="text"
      onChange={(event) => {
        setInputState(event.target.value);
      }}
      placeholder={'Ask me something'}
      value={inputState}
      onKeyPress={(event) => {
        if (event.key === "Enter" && inputState && inputState.length > 0) {
          event.preventDefault();
          setInputState('');
          addInput(inputState);
        }
      }}
    />
  );
}

export default Input;
