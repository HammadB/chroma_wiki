import React, { useCallback, useEffect, useState } from "react";
import "./App.css";
import styled from "@emotion/styled";
import { useQuery } from "@tanstack/react-query";

import Input from "./chat_components/Input";
import Chat from "./chat_components/Chat";
import { Author, ChatEntryData } from "./api/api_types";
import Header from "./Header";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  padding-right: 60px;
  padding-left: 60px;
  gap: 24px;
`;

const DEFAULT_CHAT: ChatEntryData = {
  content: "Hi there, how can I help?",
  author: Author.AGENT,
};

const CHAT_URL = "http://127.0.0.1:8000/chat/";
const CHAT_SESSION_CREATE = "http://127.0.0.1:8000/create_streaming_chat/";
const STREAMING_API_URL = "http://127.0.0.1:8000/get_streaming_chat_response";

function App() {
  const [chats, setChats] = useState([DEFAULT_CHAT]);
  const [enabledEventSource, setEnabledEventSource] = useState<boolean>(false);
  const [loadingResponse, setLoadingResponse] = useState<boolean>(false);

  const { data, refetch } = useQuery({
    queryKey: ["chat_query"],
    queryFn: () =>
      fetch(CHAT_SESSION_CREATE, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(chats.slice(1)),
        headers: {
          "Content-Type": "application/json",
        },
      }).then((res) =>
        res.json().then((data) => {
          // TODO: handle errors and ugly chaining
          setEnabledEventSource(true)
          return data;
        })
      ),
    cacheTime: 0,
    enabled: false,
    retry: false,
  });

  const addChat = useCallback(
    (new_chat: ChatEntryData) => {
      setChats((chats) => [...chats, new_chat]);
    },
    [setChats]
  );

  const updateLastChat = useCallback(
    (content: string) => {
      setChats((chats) => {
        chats[chats.length - 1].content = content;
        return [...chats]
      });
    },
    [setChats]
  );

  useEffect(() => {
    var sse: EventSource | undefined;
    if (enabledEventSource) {
      sse = new EventSource(STREAMING_API_URL, { withCredentials: true });
      sse.onmessage = (e) => {
        const parsed_chat: ChatEntryData = JSON.parse(e.data)
        if (parsed_chat.isTransient){
          updateLastChat(parsed_chat.content)
        } else {
          addChat(parsed_chat);
        }
        if (parsed_chat.isStop){
          sse?.close()
          setLoadingResponse(false);
        }
      }
      sse.onerror = () => {
        sse?.close();
        setLoadingResponse(false);
        // Add error message
      }

      setEnabledEventSource(false);
    }
    // return () => sse?.close()
  }, [enabledEventSource, addChat, updateLastChat]);


  // Note - not ideal latency-wise to issue this fetch through this useEffect -> useQuery cascade. Should just make it imperative but this is more "react-y"
  useEffect(() => {
    // Call API if last chat is user
    if (chats[chats.length - 1].author === Author.USER) {
      refetch();
      setLoadingResponse(true);
    }
  }, [chats, refetch, setLoadingResponse]);

  return (
    <>
      <Header/>
      <Container>
        <Chat chats={chats} />
        <Input
          loading={loadingResponse}
          addInput={(input) => addChat({ content: input, author: Author.USER })}
        />
      </Container>
    </>
  );
}

export default App;
