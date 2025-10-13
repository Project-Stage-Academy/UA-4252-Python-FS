type LoginProps = {
  title?: string;
};

export default function Login({ title = "🔐 Login Page" }: LoginProps) {
  return <h1>{title}</h1>;
}
