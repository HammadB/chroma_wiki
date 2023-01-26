import React from 'react';
import styled from '@emotion/styled'
import ChatEntry from './ChatEntry';
import { ChatResponse } from '../api/api_types';

const ChatWindow = styled.div`
    border-radius: 12px;
    min-height: 480px;
    max-height: 480px;
    background-color: red;
    overflow-y: scroll;
`;

interface ChatProps {
    chats: ChatResponse[];
}

function Chat({chats}: ChatProps){

    return (
        <ChatWindow>
            {chats.map((chat) => {
                return <ChatEntry chat={chat}/>
            })}
        </ChatWindow>
    )
}

export default Chat;
