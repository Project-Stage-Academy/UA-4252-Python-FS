type RegisterProps = {
  title?: string;
};

export default function Register({ title = "📝 Register Page" }: RegisterProps) {
  return <h1>{title}</h1>;
}
