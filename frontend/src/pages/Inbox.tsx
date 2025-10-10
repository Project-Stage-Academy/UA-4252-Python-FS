type InboxProps = {
  title?: string;
};

export default function Inbox({ title = "💬 Messages Inbox" }: InboxProps) {
  return <h1>{title}</h1>;
}
