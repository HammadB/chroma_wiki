import React, { useEffect, useRef } from 'react';
import styled from '@emotion/styled'
import ChatEntry from './ChatEntry';
import { ChatEntryData } from '../api/api_types';

const ChatWindow = styled.div`
    border-radius: 12px;
    min-height: 480px;
    max-height: 480px;
    overflow-y: scroll;
    border: 1px solid var(--borderColor);
`;

interface ChatProps {
    chats: ChatEntryData[];
}

function Chat({chats}: ChatProps){

    const windowRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if(windowRef.current){
            windowRef.current.scrollTop = windowRef.current.scrollHeight; 
        }
    },[chats])

    return (
        <ChatWindow ref={windowRef}>
            {chats.map((chat, index) => {
                // It is ok to use index as key here
                return <ChatEntry chat={chat} key={index}/>
            })}
        </ChatWindow>
    )
}

export default Chat;
