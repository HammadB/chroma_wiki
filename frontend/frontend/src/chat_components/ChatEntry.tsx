import React from 'react';
import styled from '@emotion/styled'
import { Author, ChatResponse } from '../api/api_types';

const colors: { [key in Author] : string} = {
    [Author.AGENT]: 'red',
    [Author.USER]: 'purple',
};

const Container = styled.div<{author: Author}>`
    min-height: 60px;
    background-color: ${(props) => colors[props.author]};
    padding: 12px;

`;

const ChatText = styled.div`
`;

interface ChatEntryProps {
    chat: ChatResponse;
}

function ChatEntry({chat}: ChatEntryProps){
    return (
        <Container author={chat.author}>
            <ChatText>{chat.content}</ChatText>
        </Container>
    )
}

export default ChatEntry;
