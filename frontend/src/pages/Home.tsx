type HomeProps = {
  title?: string;
};

export default function Home({ title = "🏠 Home Page" }: HomeProps) {
  return <h1>{title}</h1>;
}
