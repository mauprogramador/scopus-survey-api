// Success alert messages
const successMessages = {
  'en-US': {
    T01: 'CSV downloaded successfully',
    T02: 'Combinations found successfully',
    T03: 'Articles found successfully',
  },
  'pt-BR': {
    T01: 'Download do CSV com sucesso',
    T02: 'Combinações encontradas com sucesso',
    T03: 'Artigos encontradas com sucesso',
  },
};

//
const errorFeedbacks = {
  'en-US': {
    valueMissing: 'Fill in this required field',
    typeMismatch: 'Value with invalid type',
    tooLong: 'Value too long',
    tooShort: 'Value too short',
    patternMismatch: 'Value with invalid pattern',
    rangeOverflow: 'Value greater than maximum',
    rangeUnderflow: 'Value less than minimum',
  },
  'pt-BR': {
    valueMissing: 'Preencha este campo obrigatório',
    typeMismatch: 'Valor com tipo inválido',
    tooShort: 'Valor muito curto',
    tooLong: 'Valor muito longo',
    patternMismatch: 'Valor com padrão inválido',
    rangeOverflow: 'Valor maior que o máximo',
    rangeUnderflow: 'Valor menor que o mínimo',
  },
  year: {
    noInterval: 'Interval must be at least one year',
    'start-year': 'Start Year must be less than End Year',
    'end-year': 'End Year must be greater than Start Year',
  },
};

export { successMessages, errorFeedbacks };
