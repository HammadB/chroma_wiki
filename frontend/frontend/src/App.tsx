import React, { useCallback, useEffect, useState } from "react";
import "./App.css";
import styled from "@emotion/styled";
import { useQuery } from "@tanstack/react-query";

import Input from "./chat_components/Input";
import Chat from "./chat_components/Chat";
import { Author, ChatResponse } from "./api/api_types";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-right: 60px;
  padding-left: 60px;
  gap: 24px;
`;

const DEFAULT_CHAT: ChatResponse = {
  content: "Hi there, how can I help?",
  author: Author.AGENT,
};

const API_URL = "http://127.0.0.1:8000/query/";

function App() {
  const [chats, setChats] = useState([DEFAULT_CHAT]);

  const { data, refetch, isFetching } = useQuery({
    queryKey: ["chat_query"],
    queryFn: () =>
      fetch(API_URL + chats[chats.length - 1].content, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      }).then((res) => res.json().then((data) => {
        // TODO: handle errors and ugly chaining
        addChat(data.response, Author.AGENT);
        return data;
      })),
    cacheTime: 0,
    enabled: false,
    retry: false,
  });

  const addChat = useCallback((content: string, author: Author) => {
    setChats([...chats, { content: content, author: author }]);
  }, [setChats, chats]);

  // Note - not ideal latency-wise to issue this fetch through this useEffect -> useQuery cascade. Should just make it imperative but this is more "react-y"
  useEffect(() => {
    // Call API if last chat is user
    if (chats[chats.length - 1].author === Author.USER) {
      refetch();
    }
  }, [chats, refetch]);

  return (
    <Container>
      <Chat chats={chats} />
      <Input
        loading={false}
        addInput={(input) => addChat(input, Author.USER)}
      />
    </Container>
  );
}

export default App;
