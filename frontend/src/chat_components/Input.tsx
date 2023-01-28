import React, { useEffect, useRef, useState } from "react";
import styled from "@emotion/styled";

const InputContainer = styled.div`
  height: 36px;
  width: 100%;
  border-radius: 8px;
  background-color: var(--foregroundColor);
  border: 1px var(--borderColor) solid;
  padding-left: 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const InputField = styled.input`
  height: 100%;
  width: 100%;
  outline: none;
  border: none;
  background: none;
`;

const LoadingSpinnerContainer = styled.div`
  width: 24px;
  height: 24px;
`;

interface InputProps {
  addInput: (input: string) => any;
  loading: boolean;
}

function Input({ addInput, loading }: InputProps) {
  const [inputState, setInputState] = useState<string>("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!loading && inputRef.current) {
      inputRef.current?.focus();
    }
  }, [loading]);

  return (
    <InputContainer>
      {loading && (
        <LoadingSpinnerContainer>
          <div className="lds-ring">
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </div>
        </LoadingSpinnerContainer>
      )}
      <InputField
        type="text"
        onChange={(event) => {
          setInputState(event.target.value);
        }}
        placeholder={!loading ? "Ask me something" : ""}
        value={inputState}
        onKeyPress={(event) => {
          if (event.key === "Enter" && inputState && inputState.length > 0) {
            event.preventDefault();
            setInputState("");
            addInput(inputState);
          }
        }}
        disabled={loading}
        ref={inputRef}
      />
    </InputContainer>
  );
}

export default Input;
