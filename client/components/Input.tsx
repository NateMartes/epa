import Button from '@/components/Button';
export default function MyForm() {
  function handleSubmit(e) {
  
    e.preventDefault();
    const form = e.target
    const formData = new FormData(form);
    fetch('/some-api', {method: form.method, body: formData });
    const formJson = Object.fromEntries(formData.entries());
    console.log(formJson);
  }
  return (
    <form method="post" onSubmit={handleSubmit}>
      <label>
        Text input: <input name="myInput" defaultValue="Some initial value" />
      </label>
      <hr />
      <Pressable
          style={[styles.button, { backgroundColor: '#fff' }]}
          onPress={handleSubmit}>
          <FontAwesome name="paper-plane" size={18} color="#25292e" style={styles.buttonIcon} />
          <Text style={[styles.buttonLabel, { color: '#25292e' }]}>{label}</Text>
      </Pressable>
    </form>
  );
}